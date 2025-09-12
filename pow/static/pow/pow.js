class PoWValidator {
    constructor() {
        this.challenge = null;
        this.difficulty = 20;
        this.isProcessing = false;
        this.statusEl = null;
        this.clientMeta = { hasWorkers: null, hasCrypto: null, threads: null, mode: null, reason: null };
        this.lockStatus = false;
    }

    async getChallenge() {
        try {
            const response = await fetch('/pow/challenge/');
            const data = await response.json();
            this.challenge = data.challenge;
            this.difficulty = data.difficulty;
            return data;
        } catch (error) {
            console.error('Failed to get challenge:', error);
            throw error;
        }
    }

    async validateSolution(nonce, response, elapsedTime) {
        try {
            const response_data = await fetch('/pow/validate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    challenge: this.challenge,
                    nonce: nonce,
                    response: response,
                    elapsedTime: elapsedTime,
                    meta: this.clientMeta
                })
            });
            return await response_data.json();
        } catch (error) {
            console.error('Failed to validate solution:', error);
            throw error;
        }
    }

    async solveChallenge(progressCallback) {
        if (this.isProcessing) {
            throw new Error('Already processing');
        }

        this.isProcessing = true;
        const startTime = performance.now();

        try {
            await this.getChallenge();
            
            const solution = await this.calculatePoW(
                this.challenge, 
                this.difficulty, 
                progressCallback
            );
            
            const elapsedTime = (performance.now() - startTime) / 1000;
            
            const validation = await this.validateSolution(
                solution.nonce, 
                solution.hash, 
                elapsedTime
            );
            
            return validation;
        } finally {
            this.isProcessing = false;
        }
    }

    async calculatePoW(data, difficulty, progressCallback) {
        const writeStatus = (msg, level = null) => {
            try {
                if (!this.statusEl) {
                    this.statusEl = document.getElementById('pow-status') || document.querySelector('.pow-status');
                }
                if (this.statusEl) {
                    this.statusEl.textContent = msg;
                    if (level) {
                        this.statusEl.classList.remove('ok', 'warn', 'err');
                        this.statusEl.classList.add(level);
                        if (level === 'warn' || level === 'err') {
                            this.lockStatus = true;
                            window.__powStatusLocked = true;
                        } else if (level === 'ok') {
                            this.lockStatus = false;
                            window.__powStatusLocked = false;
                        }
                    }
                }
            } catch (_) {}
        };

        const hasWorkers = typeof Worker === 'function';
        const hasCrypto = typeof crypto?.subtle?.digest === 'function';
        const threads = Math.max(1, Math.floor((navigator.hardwareConcurrency || 2) / 2));
        this.clientMeta = { hasWorkers, hasCrypto, threads, mode: null, reason: null };

        if (!hasCrypto) {
            writeStatus('Нет crypto.subtle. Включи современные функции или отключи защиту.', 'warn');
            console.warn('PoW: crypto.subtle is not available; continuing, performance may be degraded');
        }

        if (!hasWorkers) {
            writeStatus('Web Workers недоступны. Отключи JShelter или включи вебворкеры. Работаю однопоточно.', 'warn');
            this.clientMeta.mode = 'single';
            this.clientMeta.reason = 'no_workers_api';
            console.info('PoW: starting in single-thread mode; reason=no_workers_api');
            return this.calculatePoWSingleThread(data, difficulty, progressCallback);
        }

        return new Promise((resolve, reject) => {
            const workers = [];
            let settled = false;

            const cleanup = () => {
                if (settled) return;
                settled = true;
                workers.forEach(w => w.terminate());
            };

            let started = 0;
            const tryStart = (i) => {
                try {
                    const worker = new Worker('/static/pow/worker.js');
                
                    worker.onmessage = (event) => {
                        if (typeof event.data === 'number') {
                            progressCallback?.(event.data);
                        } else {
                            cleanup();
                            resolve(event.data);
                        }
                    };

                    worker.onerror = () => {
                        cleanup();
                        writeStatus('Ошибка Web Worker. Отключи JShelter или включи вебворкеры. Перехожу в один поток.', 'warn');
                        this.clientMeta.mode = 'single';
                        this.clientMeta.reason = 'worker_error';
                        console.warn('PoW: worker error; falling back to single-thread');
                        this.calculatePoWSingleThread(data, difficulty, progressCallback).then(resolve).catch(reject);
                    };

                    worker.postMessage({ data, difficulty, nonce: i, threads });

                    workers.push(worker);
                    this.clientMeta.mode = 'workers';
                    started++;
                } catch (_) {
                    cleanup();
                    writeStatus('Web Workers заблокированы. Перехожу в один поток.', 'warn');
                    this.clientMeta.mode = 'single';
                    this.clientMeta.reason = 'worker_blocked_throw';
                    console.warn('PoW: worker blocked by environment; falling back to single-thread');
                    this.calculatePoWSingleThread(data, difficulty, progressCallback).then(resolve).catch(reject);
                }
            };

            for (let i = 0; i < threads; i++) tryStart(i);
            console.info(`PoW: starting with mode=${this.clientMeta.mode || 'workers'} threads=${threads}`);
        });
    }

    async calculatePoWSingleThread(data, difficulty, progressCallback) {
        const requiredZeroBytes = Math.floor(difficulty / 2);
        const isDifficultyOdd = (difficulty % 2) !== 0;
        let nonce = 0;
        let iterations = 0;

        const encoder = new TextEncoder();
        const toHex = (arr) => arr.reduce((s, b) => s + b.toString(16).padStart(2, '0'), '');

        while (true) {
            const buf = await crypto.subtle.digest('SHA-256', encoder.encode(data + nonce));
            const hash = new Uint8Array(buf);

            let ok = true;
            for (let i = 0; i < requiredZeroBytes; i++) {
                if (hash[i] !== 0) { ok = false; break; }
            }
            if (ok && isDifficultyOdd) {
                if ((hash[requiredZeroBytes] >> 4) !== 0) ok = false;
            }
            if (ok) {
                return { hash: toHex(hash), data, difficulty, nonce };
            }
            nonce += 1;
            iterations++;
            if ((iterations & 1023) === 0) progressCallback?.(nonce);
        }
    }
}

window.PoWValidator = PoWValidator;

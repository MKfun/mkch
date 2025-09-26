// Utils functions:

function urlBase64ToUint8Array (base64String) {
  var padding = '='.repeat((4 - base64String.length % 4) % 4)
  var base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/')

  console.log(rawData);
  var rawData = window.atob(base64)
  var outputArray = new Uint8Array(rawData.length)

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray;
}

var applicationServerKey = 'BCp70uFVTIAKbHiIFt2RFzAnPCdT73HymDfij-j0ABtxj5C9Xrkj3122744xsfa3zaaTkBuqPGoFkedar4GF6so';

function subscribeUser() {
  if ('Notification' in window && 'serviceWorker' in navigator) {
    console.log("Registering service worker...");
    navigator.serviceWorker.register("/static/js/worker.js").then(function (reg) {
    console.log("Done!");
      reg.pushManager
        .subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(
            applicationServerKey
          ),
        })
        .then(function (sub) {
          var registration_id = sub.endpoint;
          var data = {
            p256dh: btoa(
              String.fromCharCode.apply(
                null,
                new Uint8Array(sub.getKey('p256dh'))
              )
            ),
            auth: btoa(
              String.fromCharCode.apply(
                null,
                new Uint8Array(sub.getKey('auth'))
              )
            ),
            registration_id: registration_id,
          }
          requestPOSTToServer(data)
        })
        .catch(function (e) {
          if (Notification.permission === 'denied') {
            console.warn('Permission for notifications was denied')
          } else {
            console.error('Unable to subscribe to push', e)
          }
        })
    })
  }
}

// Send the subscription data to your server
function requestPOSTToServer (data) {
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');
  headers.set('X-CSRFToken', Cookies.get('csrftoken'));

  const requestOptions = {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  };

  return (
    fetch(
      '/notify/register',
      requestOptions
    )
  ).then((response) => response.json())
}

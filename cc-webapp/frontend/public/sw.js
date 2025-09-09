self.addEventListener('push', function (event) {
    let data = {};
    try {
        data = event.data ? event.data.json() : {};
    } catch (e) {
        try { data = { message: event.data && event.data.text ? event.data.text() : '' }; } catch { }
    }
    const title = (data && (data.title || data.type)) || '알림';
    const body = (data && (data.message || data.body)) || '';
    const options = {
        body,
        icon: '/icons/icon-192.png',
        badge: '/icons/icon-96.png',
        data
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    const url = (event.notification && event.notification.data && event.notification.data.url) || '/notifications';
    event.waitUntil(clients.matchAll({ type: 'window' }).then(function (clientList) {
        for (const client of clientList) {
            if ('focus' in client) return client.focus();
        }
        if (clients.openWindow) return clients.openWindow(url);
    }));
});

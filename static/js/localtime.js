document.querySelectorAll('time[datetime]').forEach((el) => {
    const date = new Date(el.getAttribute('datetime'));
    el.textContent = date.toLocaleString(undefined, {month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit'});

});
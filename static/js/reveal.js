const revealEls = document.querySelectorAll('.reveal');

if('IntersectionObserver' in window && revealEls.length)
{
    const observer = new IntersectionObserver((entries, obs) =>
    {
        entries.forEach((entry) =>
        {
            if(entry.isIntersecting)
            {
                entry.target.classList.add('is-visible')
                obs.unobserve(entry.target);
                //Reveal once, then stop watching
            }
        });
    }, {threshold: 0.12});
    revealEls.forEach((el) => observer.observe(el));
}
else
{
    revealEls.forEach((el) => el.classList.add('is-visible'));
}
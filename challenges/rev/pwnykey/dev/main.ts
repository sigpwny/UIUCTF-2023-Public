import { fetch } from "@devicescript/net"

const charset = "0123456789ABCDFGHJKLMNPQRSTUWXYZ"
const key = (await (await fetch("http://localhost/check")).text()).trim()
if (key.length !== 25)
    throw new Error("Invalid key")
// "YANXA-Z2AGG-3TC8C-FBP2U-0ANCZ"
const groups = key.split("-")
if (groups.length !== 5)
    throw new Error("Invalid key")
if (groups.some(g => g.length !== 5))
    throw new Error("Invalid key")
if (groups.some(g => g.split("").some(c => !charset.includes(c))))
    throw new Error("Invalid key")

const [g1, g2, g3, g4, g5] = groups.map(g => g.split("").map(c => charset.indexOf(c)))

if (`${g1}` !== `${[30, 10, 21, 29, 10]}`)
    throw new Error("Invalid key")  

function concat(a: number[], b: number[]) {
    const result = []
    for (let i = 0; i < a.length; i++)
        result.push(a[i])
    for (let i = 0; i < b.length; i++)
        result.push(b[i])
    return result
}

const check2 = concat(g2, g3)

if (check2.reduce((a, b) => a + b) !== 134 || check2.reduce((a, b) => a * b, 1) !== 12534912000)
    throw new Error("Invalid key")

let check3 = g4
let ctr = 1337
function nextInt() {
    let t = check3.pop()
    t ^= (t >> 2) & 0xffffffff
    t ^= (t << 1) & 0xffffffff
    t ^= (check3[0] ^ (check3[0] << 4)) & 0xffffffff
    ctr = (ctr + 13371337) & 0xffffffff
    check3.unshift(t)
    return t + ctr
}
for (let i = 0; i < 1337; i++) {
    nextInt()
}
console.log(`${[nextInt(),nextInt(),nextInt()]}`);
if (`${[nextInt(),nextInt(),nextInt()]}` !== `${[793639219, -745864865, 532305874]}`)
    throw new Error("Invalid key")

console.log("OK")

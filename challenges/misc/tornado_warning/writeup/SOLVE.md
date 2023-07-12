# About the Challenge
This challenge aims to teach people about [SAME](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding), the encoding scheme that lets the US Emergency Alert System communicate data to weather radios and broadcast stations. SAME headers sound like three buzzes before the voice part of a weather radio alert. The same data is sent three times in a row so that weather radios can implement byte-by-byte best-two-out-of-three error checking.

# Solution
To solve this challenge, you'll need to demodulate a SAME header that has a bunch of errors, isolate the errors, and read them. Most off-the-shelf demodulators either completely fail at this task (I couldn't get [multimon-ng](https://github.com/EliasOenal/multimon-ng/) to work on this recording), or they've already implemented error-checking and they don't let you see the errors (like [sameold](https://github.com/cbs228/sameold)).

There are a few ways to demodulate the headers with errors intact:

- Write your own demodulator or manually demodulate (hardest)
- Take apart an existing demodulator and remove the error-checking parts, recompile and run (pretty hard, depending on demodulator)
- Cut and paste the audio in an audio editor to make "fake headers" that off-the-shelf demodulators will understand (fairly easy, intended solve)
- Find a demodulator that doesn't implement error-checking (kind of guessy but easy once you have one)

In the solve script, I used [nwsrx](http://www.kk5jy.net/nwsrx-v1/), a demodulator without error-checking. If you used a different method, look at the comments in the script. 

After getting the three headers, do the inverse of best-two-out-of-three error checking. Go index by index and look for the "odd character out" between the three headers. Reading these characters, you'll get the flag, padded by some space at the beginning and end without any errors.

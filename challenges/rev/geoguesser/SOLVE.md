# Solve

Using janet's built in features for disassembly is helpful:
```
$ janet
Janet 1.28.0-358f5a0 linux/x64/gcc - '(doc)' for help
repl:1:> (load-image (slurp "program.jimage"))
@{compare-coord @{:doc "(compare-coord a b tolerance)\n\n" :source-map ("main.janet" 32 1) :value <function compare-coord>} compare-float @{:doc "(compare-float a b tolerance)\n\n" :source-map ("main.janet" 29 1) :value <function compare-float>} coordinate-peg @{:source-map ("main.janet" 8 1) :value { :float (number (some (+ :d (set ".-+")))) :main (* :ss :float :sep :float :ss) :sep (* :ss "," :ss) :ss (any :s)}} get-guess @{:doc "(get-guess)\n\n" :source-map ("main.janet" 21 1) :value <function get-guess>} guessing-game @{:doc "(guessing-game answer)\n\n" :source-map ("main.janet" 36 1) :value <function guessing-game>} init-rng @{:doc "(init-rng)\n\n" :source-map ("main.janet" 5 1) :value <function init-rng>} main @{:doc "(main &)\n\n" :source-map ("main.janet" 54 1) :value <function main>} parse-coord @{:doc "(parse-coord s)\n\n" :source-map ("main.janet" 15 1) :value <function parse-coord>} precision @{:source-map ("main.janet" 1 1) :value 0.0001} print-flag @{:doc "(print-flag)\n\n" :source-map ("main.janet" 46 1) :value <function print-flag>} random-float @{:doc "(random-float min max)\n\n" :source-map ("main.janet" 51 1) :value <function random-float>} rng @{:ref @[nil] :source-map ("main.janet" 3 1)} :current-file "main.janet" :macro-lints @[] :source "main.janet"}
```

From there, it's a straightforward path to figuring out that the rng is seeded by the current time.

Probably the easiest way to solve it is to write another janet program similar to this one to generate random values (see healthcheck/solve.janet)

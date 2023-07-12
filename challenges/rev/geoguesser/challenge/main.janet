(def precision 1e-4)

(var rng nil)

(defn init-rng []
  (set rng (math/rng (os/time))))

(def coordinate-peg
  '{:main (* :ss :float :sep :float :ss)
    :float (number (some (+ :d (set ".-+"))))
    :ss (any :s)
    :sep (* :ss "," :ss)})

# coordinate parser (ex: 32, -123.4)
(defn parse-coord [s]
  (if-let [[lat lon] (peg/match coordinate-peg s)]
    (if (and (<= -90 lat 90) (<= -180 lon 180))
      [lat lon]
      nil)))

(defn get-guess []
  (prin "Where am I? ")
  (if-let [input-line (file/read stdin :line)
           num (parse-coord input-line)]
    num
    (do (print "Not a valid coordinate. Try again.")
        (get-guess))))

(defn compare-float [a b tolerance]
  (< (math/abs (- a b)) tolerance))

(defn compare-coord [a b tolerance]
  (and (compare-float (get a 0) (get b 0) tolerance)
       (compare-float (get a 1) (get b 1) tolerance)))

(defn guessing-game [answer]
  (var guess (get-guess))
  (var remaining 4)
  (while (and (not (compare-coord guess answer precision))
              (> remaining 0))
    (print "Nope. You have " remaining " guesses left.")
    (-- remaining)
    (set guess (get-guess)))
  (compare-coord guess answer precision))

(defn print-flag []
  (def f (file/open "/flag.txt"))
  (print "You win!")
  (print "The flag is: " (string/trimr (file/read f :all))))

(defn random-float [min max]
  (+ min (* (math/rng-uniform rng) (- max min))))

(defn main [&]
  (print "Welcome to geoguesser!")
  (init-rng)
  (def answer [(random-float -90 90) (random-float -180 180)])
  (if (guessing-game answer)
    (print-flag)
    (do
      (print "You lose!")
      (print "The answer was: " answer))))

(defn random-float [rng min max]
  (+ min (* (math/rng-uniform rng) (- max min))))

# we know that the rng is seeded with the time, so we can just do something similar
(defn main [&]
  (def now (os/time))
  (loop [delta :range [-1 2]]
    (def rng (math/rng (+ now delta)))
    (def [lat long] [(random-float rng -90 90) (random-float rng -180 180)])
    (printf "%.5f,%.5f" lat long)))

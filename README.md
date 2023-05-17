# SimInhale Project helpers

## Using scripts

### Deposition fractions Plot ([`deposition_fraction.py`](./scripts/deposition_fraction.py))

Plots deposition fraction from a csv containing positions of particles and their status

``` shell
  python deposition_fraction.py <latest particle position csv> <save/show> <particle diameter>
```

- `save/show` -> optional, default is `show`
- `particle diameter` -> optional, default is `4.3`; `0` -> don't add from paper

### Splitting solutions by deposition ([`split_particles.py`](./scripts/split_particles.py))

Generates csv files by splitting each csv into csv containing **deposited** and **non-deposited** particles

``` shell
  python split_particles.py <folder containing particles csv>
```

### Converting video into gif ([`convert.sh`](./scripts/convert.sh))

Speeds up and converts an `webm` file into a `gif`. (It is recommended to view the script and use the commands in it as per requirement)

``` shell
  sh convert.sh <video>
```

### MLFlow tracking ([`track.py`](./scripts/track.py))

Tracks a fluid/particle simulation

``` shell
  python track.py <experiment> <outputDirectory> <datFile> --runShell <True/False> --executable <executableName> --args <comma separated extra arguments>
```


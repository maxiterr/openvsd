#!/usr/bin/env bats


@test "Check that the vsd client is available" {
    command -v vsd
}


@test "invoking vsd without command prints usage" {
  run vsd
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}



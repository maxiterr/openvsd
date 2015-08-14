#!/usr/bin/env bats

APIKey=~/.vsd/APIKey

setup() {
    export VSD_USERNAME=test
    export VSD_PASSWORD=test
    export VSD_ENTERPRISE=test
    export VSD_URL=http://localhost:5000/nuage/api/v1_0/
}


@test "VSD client is available" {
    command -v vsd
}


@test "Invoking vsd without command prints usage" {
    run vsd
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}


@test "Invoking vsd with wrong command prints usage" {
    run vsd azertyuiop
    [ "$status" -ne 0 ]
    [ "${lines[0]}" = "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}


@test "Run vsd with debug option" {
    run vsd --debug me-show
    [ "$status" -eq 0 ]
    [ $(expr "${lines[1]}" : "# Request") -ne 0 ]
    [ $(expr "${lines[2]}" : "# Method: ") -ne 0 ]
    [ $(expr "${lines[3]}" : "# URL: ") -ne 0 ]
    [ $(expr "${lines[4]}" : "# Headers: ") -ne 0 ]
    [ $(expr "${lines[5]}" : "# Parameters: ") -ne 0 ]
    [ $(expr "${lines[7]}" : "# Response") -ne 0 ]
    [ $(expr "${lines[8]}" : "# Status code: ") -ne 0 ]
    [ $(expr "${lines[9]}" : "# Headers: ") -ne 0 ]
    [ $(expr "${lines[10]}" : "# Body: ") -ne 0 ]
}


@test "Test authentication and create APIkey file" {
    if [ -f ${APIKey} ]; then
        rm -f ${APIKey}
    fi
    [ ! -f ${APIKey} ]

    run vsd enterprise-list

    [ "$status" -eq 0 ]
    [ -f ${APIKey} ]
}


@test "Second connexion without authentication" {
    [ -f ${APIKey} ]
    run vsd --debug enterprise-list
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*/nuage/api/v1_0/me.*") -eq 0  ]
}


@test "Force authentication" {
    [ -f ${APIKey} ]
    run vsd --debug --force-auth enterprise-list
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*/nuage/api/v1_0/me") -ne 0  ]
}


@test "Make wrong authentication" {
    run vsd --vsd-username zedzedzed me-show
    [ "$status" -ne 0 ]
    [ "${lines[0]}" = "Error: Athentication failed. Please verify your credentials." ]
}


@test "enterprise-list" {
    run vsd enterprise-list
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e *| *nulab-1.*") -ne 0  ]
    [ $(expr "${output}" : ".*5b2cc2f3-2b86-42ec-892d-edde741b2fd4 *| *nulab-2.*") -ne 0  ]
}


@test "enterprise-list with --filter" {
    run vsd enterprise-list --filter 92a76e6f-2ac4
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e *| *nulab-1.*") -ne 0  ]
    [ $(expr "${output}" : ".*5b2cc2f3-2b86-42ec-892d-edde741b2fd4 *| *nulab-2.*") -eq 0  ]
}


@test "enterprise-show" {
    run vsd enterprise-show 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *nulab-1.*") -ne 0  ]
    [ $(expr "${output}" : ".*ID *| *92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e.*") -ne 0  ]
}


@test "enterprise-create new-enterprise" {
    run vsd enterprise-create new-enterprise
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *new-enterprise.*") -ne 0  ]
    [ $(expr "${output}" : ".*ID *| *255d9673-7281-43c4-be57-fdec677f6e07.*") -ne 0  ]
}


@test "Re-try create new-enterprise must fail" {
    run vsd enterprise-create new-enterprise
    [ "$status" -ne 0 ]
    [  $(expr "${lines[0]}" : "Error: Object already exists.") -ne 0 ]
}


@test "Delete existing enterprise" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    [ "$status" -eq 0 ]
    [  "x${output}" == "x" ]
}

@test "Delete non existing enterprise" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    [ "$status" -ne 0 ]
    [  $(expr "${lines[0]}" : "Error: Cannot find object with ID") -ne 0 ]
}


@test "Create enterprise new-enterprise with show-only" {
    run vsd --show-only ID enterprise-create new-enterprise
    [ "$status" -eq 0 ]
    [ ${lines[0]} == "255d9673-7281-43c4-be57-fdec677f6e07"  ]
}


@test "Update enterprise name" {
    run vsd enterprise-update 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --key-value name:nulab-update
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *nulab-update .*") -ne 0  ]
}

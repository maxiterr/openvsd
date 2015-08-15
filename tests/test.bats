#!/usr/bin/env bats

APIKey=~/.vsd/APIKey

setup() {
    export VSD_USERNAME=test
    export VSD_PASSWORD=test
    export VSD_ENTERPRISE=test
    export VSD_URL=http://localhost:5000/nuage/api/v1_0/
}


@test "VSD client: is available" {
    command -v vsd
}


@test "VSD client: invoking without command prints usage" {
    run vsd
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}


@test "VSD client: invoking with wrong command prints usage" {
    run vsd azertyuiop
    [ "$status" -ne 0 ]
    [ "${lines[0]}" = "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}


@test "VSD client: run with debug option" {
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


@test "VSD client: test authentication and create APIkey file" {
    if [ -f ${APIKey} ]; then
        rm -f ${APIKey}
    fi
    [ ! -f ${APIKey} ]

    run vsd enterprise-list

    [ "$status" -eq 0 ]
    [ -f ${APIKey} ]
}


@test "VSD client: second connexion without authentication" {
    [ -f ${APIKey} ]
    run vsd --debug enterprise-list
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*/nuage/api/v1_0/me.*") -eq 0 ]
}


@test "VSD client: force authentication" {
    [ -f ${APIKey} ]
    run vsd --debug --force-auth enterprise-list
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*/nuage/api/v1_0/me") -ne 0 ]
}


@test "VSD client: make wrong authentication" {
    run vsd --vsd-username zedzedzed me-show
    [ "$status" -ne 0 ]
    [ "${lines[0]}" = "Error: Athentication failed. Please verify your credentials." ]
}


@test "Enterprise: list" {
    run vsd enterprise-list
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e *| *nulab-1.*") -ne 0 ]
    [ $(expr "${output}" : ".*5b2cc2f3-2b86-42ec-892d-edde741b2fd4 *| *nulab-2.*") -ne 0 ]
}


@test "Enterprise: list with filter" {
    run vsd enterprise-list --filter 92a76e6f-2ac4
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e *| *nulab-1.*") -ne 0 ]
    [ $(expr "${output}" : ".*5b2cc2f3-2b86-42ec-892d-edde741b2fd4 *| *nulab-2.*") -eq 0 ]
}


@test "Enterprise: show" {
    run vsd enterprise-show 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *nulab-1.*") -ne 0 ]
    [ $(expr "${output}" : ".*ID *| *92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e.*") -ne 0 ]
}


@test "Enterprise: create" {
    run vsd enterprise-create new-enterprise
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *new-enterprise.*") -ne 0 ]
    [ $(expr "${output}" : ".*ID *| *255d9673-7281-43c4-be57-fdec677f6e07.*") -ne 0 ]
}


@test "Enterprise: create existing must fail" {
    run vsd enterprise-create new-enterprise
    [ "$status" -ne 0 ]
    [  $(expr "${lines[0]}" : "Error: Object already exists.") -ne 0 ]
}


@test "Enterprise: delete existing" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    [ "$status" -eq 0 ]
    [  "x${output}" == "x" ]
}

@test "Enterprise: delete non existing" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    [ "$status" -ne 0 ]
    [  $(expr "${lines[0]}" : "Error: Cannot find object with ID") -ne 0 ]
}


@test "Enterprise: create with show-only" {
    run vsd --show-only ID enterprise-create new-enterprise
    [ "$status" -eq 0 ]
    [ ${lines[0]} == "255d9673-7281-43c4-be57-fdec677f6e07" ]
}


@test "Enterprise: update name" {
    run vsd enterprise-update 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --key-value name:nulab-update
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *nulab-update .*") -ne 0 ]
}


@test "Domain template: create" {
    run vsd domaintemplate-create DomainTemplate-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *DomainTemplate-1 .*") -ne 0  ]
    [ $(expr "${output}" : ".*ID *| *255d9673-7281-43c4-be57-fdec677f6e07.*") -ne 0  ]
}


@test "Domain template: list" {
    run vsd domaintemplate-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*255d9673-7281-43c4-be57-fdec677f6e07 *| *DomainTemplate-1.*") -ne 0  ]
}


@test "Domain template: list with filter" {
    run vsd domaintemplate-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter DomainTemplate
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*255d9673-7281-43c4-be57-fdec677f6e07 *| *DomainTemplate-1.*") -ne 0  ]

    run vsd domaintemplate-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter NoDomain
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*255d9673-7281-43c4-be57-fdec677f6e07 *| *DomainTemplate-1.*") -eq 0  ]
}


@test "Domain template: show" {
    run vsd domaintemplate-show 255d9673-7281-43c4-be57-fdec677f6e07
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *DomainTemplate-1 .*") -ne 0  ]
    [ $(expr "${output}" : ".*ID *| *255d9673-7281-43c4-be57-fdec677f6e07.*") -ne 0  ]
}


@test "Domain template: update name" {
    run vsd domaintemplate-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value name:domainTemplate-update
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *domainTemplate-update .*") -ne 0  ]
}


@test "Domain template: delete" {
    run vsd domaintemplate-delete 255d9673-7281-43c4-be57-fdec677f6e07
    [ "$status" -eq 0 ]

    run vsd domaintemplate-show 255d9673-7281-43c4-be57-fdec677f6e07
    [ "$status" -eq 0 ]
    [ $(expr "${output}" : ".*name *| *domainTemplate.*") -eq 0  ]
}


@test "Domain template: Create domain with show-only" {
    run vsd --show-only ID domaintemplate-create DomainTemplate-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    [ "$status" -eq 0 ]
    [ ${lines[0]} == "255d9673-7281-43c4-be57-fdec677f6e07"  ]
}

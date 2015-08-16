#!/usr/bin/env bats

APIKey=~/.vsd/APIKey

load helpers

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
    assert_success
    assert_line_contains 0 "Usage: vsd [OPTIONS] COMMAND [ARGS]..."
}


@test "VSD client: invoking with wrong command prints usage" {
    run vsd azertyuiop
    assert_fail
    assert_line_contains 0 "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}


@test "VSD client: run with debug option" {
    run vsd --debug me-show
    assert_success
    assert_line_contains 1 "# Request"
    assert_line_contains 2 "# Method: "
    assert_line_contains 3 "# URL: "
    assert_line_contains 4 "# Headers: "
    assert_line_contains 5 "# Parameters: "
    assert_line_contains 7 "# Response"
    assert_line_contains 8 "# Status code: "
    assert_line_contains 9 "# Headers: "
    assert_line_contains 10 "# Body: "
}


@test "VSD client: test authentication and create APIkey file" {
    if [ -f ${APIKey} ]; then
        rm -f ${APIKey}
    fi
    [ ! -f ${APIKey} ]

    run vsd enterprise-list
    assert_success
    [ -f ${APIKey} ]
}


@test "VSD client: second connexion without authentication" {
    [ -f ${APIKey} ]
    run vsd --debug enterprise-list
    assert_success
    assert_output_not_contains "/nuage/api/v1_0/me"
}


@test "VSD client: force authentication" {
    [ -f ${APIKey} ]
    run vsd --debug --force-auth enterprise-list
    assert_success
    assert_output_contains "/nuage/api/v1_0/me"
}


@test "VSD client: make wrong authentication" {
    run vsd --vsd-username bad-user me-show
    assert_fail
    assert_line_contains 0 "Error: Athentication failed. Please verify your credentials."
}


@test "Enterprise: list" {
    run vsd enterprise-list
    assert_success
    assert_output_contains_in_table 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e nulab-1
    assert_output_contains_in_table 5b2cc2f3-2b86-42ec-892d-edde741b2fd4 nulab-2
}


@test "Enterprise: list with filter" {
    run vsd enterprise-list --filter 92a76e6f-2ac4
    assert_success
    assert_output_contains_in_table 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e nulab-1
    assert_output_not_contains_in_table 5b2cc2f3-2b86-42ec-892d-edde741b2fd4 nulab-2
}


@test "Enterprise: show" {
    run vsd enterprise-show 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table name nulab-1
    assert_output_contains_in_table ID 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
}


@test "Enterprise: create" {
    run vsd enterprise-create new-enterprise
    assert_success
    assert_output_contains_in_table name new-enterprise
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Enterprise: create existing must fail" {
    run vsd enterprise-create new-enterprise
    assert_fail
    assert_line_contains 0 "Error: Object already exists."
}


@test "Enterprise: delete existing" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    assert_success
    assert_output_empty
}

@test "Enterprise: delete non existing" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    assert_fail
    assert_line_contains 0 "Error: Cannot find object with ID"
}


@test "Enterprise: create with show-only" {
    run vsd --show-only ID enterprise-create new-enterprise
    assert_success
    assert_line_equals 0 "255d9673-7281-43c4-be57-fdec677f6e07"
}


@test "Enterprise: update name" {
    run vsd enterprise-update 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --key-value name:nulab-update
    assert_success
    assert_output_contains name nulab-update
}


@test "License: create" {
    run vsd license-create 12Z1223E23E23E23E23E23OMEX2KEOJ3EPOJ2A3EPXJP34RJC4P5IOJVPOIYJECEOP4XJPRO4JC5SRVDCOTJQXZQJ4PCJT5P
    assert_success
    assert_output_contains company Compagny-1
    assert_output_not_contains license
}


@test "License: show" {
    run vsd license-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains company Compagny-1
    assert_output_not_contains license
}


@test "License: show with verbose" {
    run vsd license-show 255d9673-7281-43c4-be57-fdec677f6e07 --verbose
    assert_success
    assert_output_contains company Compagny-1
    assert_output_not_contains license
    assert_line_contains -1 "License: 12Z1223E23E2"
}


@test "License: list" {
    run vsd license-list
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Compagny-1
}


@test "License: delete" {
    run vsd license-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    assert_success
    assert_output_empty
    run vsd license-list
    assert_success
    assert_output_not_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Compagny-1
}


@test "Domain template: create" {
    run vsd domaintemplate-create DomainTemplate-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table name DomainTemplate-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Domain template: list" {
    run vsd domaintemplate-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 DomainTemplate-1
}


@test "Domain template: list with filter" {
    run vsd domaintemplate-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter DomainTemplate
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 DomainTemplate-1

    run vsd domaintemplate-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter NoDomain
    assert_success
    assert_output_not_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 DomainTemplate-1
}


@test "Domain template: show" {
    run vsd domaintemplate-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name DomainTemplate-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Domain template: update name" {
    run vsd domaintemplate-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value name:domainTemplate-update
    assert_success
    assert_output_contains_in_table name domainTemplate-update
}


@test "Domain template: delete" {
    run vsd domaintemplate-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
    run vsd domaintemplate-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_not_contains domainTemplate
}


@test "Domain template: Create with show-only" {
    run vsd --show-only ID domaintemplate-create DomainTemplate-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Domain: create without enterprise" {
    run vsd domain-create Domain-1 --template-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_output_contains "Error: Missing option \"--enterprise-id\"."
}


@test "Domain: create without template" {
    run vsd domain-create Domain-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_fail
    assert_output_contains "Error: Missing option \"--template-id\""
}


@test "Domain: create without name" {
    run vsd domain-create --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --template-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_output_contains "Error: Missing argument \"name\""
}


@test "Domain: create" {
    run vsd domain-create Domain-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --template-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Domain-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Domain: update" {
    run vsd domain-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeTarget:65000 --key-value routeDistinguisher:100
    assert_success
    assert_output_contains_in_table routeTarget 65000
    assert_output_contains_in_table routeDistinguisher 100
}


@test "Domain: list for a given enterprise" {
    run vsd domain-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Domain-1
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 "65000 / 100"
}


@test "Domain: list for a given domain template" {
    run vsd domain-list --domaintemplate-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Domain-1
}


@test "Domain: list with filter" {
    run vsd domain-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter Domain
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Domain-1

    run vsd domain-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter noDomain
    assert_success
    assert_output_not_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e0 Domain-1
}


@test "Domain: show" {
    run vsd domain-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Domain-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Domain: delete" {
    run vsd domain-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty

    run vsd domain-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_not_contains_in_table name domainTemplate
}


@test "Domain: Create domain with show-only" {
    run vsd --show-only ID domain-create Domain-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --template-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_line_contains 0 255d9673-7281-43c4-be57-fdec677f6e07
    vsd domain-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeTarget:65000 --key-value routeDistinguisher:100
}


@test "Zone: create without missing element" {
    run vsd zone-create Zone-1
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--domain-id\"."

    run vsd zone-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"name\"."
}


@test "Zone: create" {
    run vsd zone-create Zone-1 --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Zone-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Zone: update" {
    skip "Update command doesn't exist yet"
    run vsd zone-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value name:Zone-update
    assert_success
    assert_output_contains_in_table name Zone-update
}


@test "Zone: list for a given domain" {
    run vsd zone-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Zone-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Zone: list with filter" {
    run vsd zone-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter Zone
    assert_success
    assert_output_contains 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd zone-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter noZone
    assert_success
    assert_output_not_contains 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Zone: show" {
    run vsd zone-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Zone-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Zone: delete" {
    run vsd zone-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd zone-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_not_contains 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Zone: create with show-only" {
    run vsd --show-only ID zone-create Zone-1 --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}
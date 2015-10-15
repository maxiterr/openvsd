#!/usr/bin/env bats

# Copyright 2015 Maxime Terras <maxime.terras@numergy.com>
# Copyright 2015 Pierre Padrixe <pierre.padrixe@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


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
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Domain template: Create with show-only" {
    run vsd --show-only ID domaintemplate-create DomainTemplate-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Domain: create without missing element" {
    run vsd domain-create Domain-1 --template-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--enterprise-id\"."

    run vsd domain-create Domain-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--template-id\"."

    run vsd domain-create --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --template-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"name\"."
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


@test "Domain: delete" {
    run vsd domain-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd domain-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Domain: create with rt/rd" {
    run vsd domain-create Domain-1 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --template-id 255d9673-7281-43c4-be57-fdec677f6e07 --rt 65000 --rd 100
    assert_success
    assert_output_contains_in_table name Domain-1
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


@test "Domain: create with show-only" {
    vsd domain-delete 255d9673-7281-43c4-be57-fdec677f6e07
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
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Zone: create with show-only" {
    run vsd --show-only ID zone-create Zone-1 --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: create without missing element" {
    run vsd subnet-create --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --netmask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"name\"."

    run vsd subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--netmask\"."

    run vsd subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --netmask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--address\"."

    run vsd subnet-create Subnet-1 --address 192.168.0.0 --netmask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--zone-id\"."
}


@test "Subnet: create" {
    run vsd subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --netmask 255.255.255.0
    assert_success
    assert_output_contains_in_table name Subnet-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: update" {
    run vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value netmask:255.255.255.0 --key-value gateway:192.168.0.1
    assert_success
    assert_output_contains_in_table netmask 255.255.255.0
    assert_output_contains_in_table gateway 192.168.0.1

    # Make this subnet valid because mock doesn't create those values
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeTarget:65000
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeDistinguisher:100
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value externalID:255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: list for a given zone" {
    run vsd subnet-list --zone-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Subnet-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: list for a given domain" {
    run vsd subnet-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Subnet-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: list with filter" {
    run vsd subnet-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter Subnet
    assert_success
    assert_output_contains 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd subnet-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter noSubnet
    assert_success
    assert_output_not_contains 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: show" {
    run vsd subnet-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Subnet-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: delete" {
    run vsd subnet-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd subnet-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Subnet: Create with show-only" {
    run vsd --show-only ID subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --netmask 255.255.255.0
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
    # Make this subnet valid because mock doesn't create those values
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeTarget:65000
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeDistinguisher:100
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value externalID:255d9673-7281-43c4-be57-fdec677f6e07
}


@test "User: create with missing element" {
    run vsd user-create --firstname john --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"username\"."

    run vsd user-create jdoe --firstname john --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--lastname\"."

    run vsd user-create jdoe --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--firstname\"."

    run vsd user-create jdoe --lastname doe --firstname john --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--email\"."

    run vsd user-create jdoe --lastname doe --firstname john --email john.doe@nomail.com --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--password\"."

    run vsd user-create jdoe --lastname doe --firstname john --email john.doe@nomail.com --password xDz3R
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--enterprise-id\"."
}

@test "User: create" {
    run vsd user-create jdoe --firstname john --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table userName jdoe
    assert_output_contains_in_table email john.doe@nomail.com
    assert_output_contains_in_table firstName john
    assert_output_contains_in_table lastName doe
}

@test "User: show" {
    run vsd user-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table userName jdoe
    assert_output_contains_in_table email john.doe@nomail.com
    assert_output_contains_in_table firstName john
    assert_output_contains_in_table lastName doe
}

@test "User: delete" {
    run vsd user-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
    run vsd user-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_contains 0 "Error: Cannot find object with ID"
}

@test "User: create with --show-only" {
    run vsd --show-only ID user-create jdoe --firstname john --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}

@test "Group: create with missing elements" {
    run vsd group-create --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"name\"."

    run vsd group-create group-1
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--enterprise-id\"."
}

@test "Group: create" {
    run vsd group-create group-1 --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07 --description "Test Group"
    assert_success
    assert_output_contains_in_table name group-1
    # ToDo (pierrepadrixe): description not working
    #assert_output_contains_in_table description "Test Group"
}

@test "Group: show" {
    run vsd group-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name group-1
    # ToDo (pierrepadrixe): description not working
    #assert_output_contains_in_table description "Test Group"
}

@test "Group: update" {
    run vsd group-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value "description:Test Group"
    assert_success
    assert_output_contains_in_table description "Test Group"
}

@test "Group: delete" {
    #skip "Group-delete command doesn't exist yet"
    run vsd group-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    run vsd group-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_contains 0 "Error: Cannot find object with ID"
}

@test "Group: create with --show-only" {
    run vsd group-create group-1 --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07 --description "Test Group"
    assert_success
    assert_output_contains_in_table name group-1
    # ToDo (pierrepadrixe): description not working1
    #assert_output_contains_in_table description "Test Group"
}

@test "Group: add user in group with missing elements" {
    run vsd group-add-user --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"group-id\"."

    run vsd group-add-user 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--user-id\"."
}

@test "Group: add user in group" {
    run vsd group-add-user 255d9673-7281-43c4-be57-fdec677f6e07 --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
}

@test "Group: delete user in group with missing elements" {
    run vsd group-del-user --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"group-id\"."

    run vsd group-del-user 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--user-id\"."
}

@test "Group: delete user in group" {
    run vsd group-del-user 255d9673-7281-43c4-be57-fdec677f6e07 --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
}

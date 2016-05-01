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


load helpers
source common.bash


@test "Pep8: vsd_domain.py" {
    command pep8 --first ../open_vsdcli/vsd_domain.py
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

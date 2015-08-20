escape_string() {
    echo "$1" | sed 's#[]\/$*.^|[]#\\&#g'
}


assert_success() {
    [ "$status" -eq 0 ]
}


assert_fail() {
    [ "$status" -ne 0 ]
}


assert_output_contains() {
    STRING_1=$(escape_string "$1")
    [ $(echo "$output" | grep -c -e "$STRING_1") -ne 0 ]
}


assert_output_not_contains() {
    STRING_1=$(escape_string "$1")
    [ $(echo "$output" | grep -c -e "$STRING_1") -eq 0 ]
}


assert_output_empty() {
    [ "$output" == "" ]
}


get_in_array() {
    if [ $1 -lt 0 ]; then
        length=${#lines[@]}
        position=$((length + $1))
        echo -n "${lines[$position]}"
    else
        echo -n "${lines[$1]}"
    fi
    return 0
}


assert_line_contains() {
    STRING_2=$(escape_string "$2")
    [ $(echo "$(get_in_array $1)" | grep -c -e "$STRING_2") -eq 1 ]
}


assert_line_not_contains() {
    STRING_2=$(escape_string "$2")
    [ $(echo "${lines[$1]}" | grep -c -e "$STRING_2") -eq 0 ]
}


assert_line_equals() {
    [ "${lines[$1]}" == "$2" ]
}


# Insert '| cat' at the end to prevent bats to catch last command error
assert_output_contains_in_table() {
    result="${output}"
    for string in "$@"; do
        escaped_string=$(escape_string "${string}")
        result=$(echo "$result" | grep -e "| *$escaped_string *|" | cat)
    done
    echo "$result"
    [ "${result}" != "" ]
}


assert_output_not_contains_in_table() {
    result=$(assert_output_contains_in_table $@ | cat)
    [ "${result}" == "" ]
}

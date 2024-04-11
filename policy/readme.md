# **Conference configuration**

For each section of the conference configuration, you must enter the regex that will be matched against the dial string.  Each section also contains a "response" section, which is the starting point for the external policy.
The conference configuration must contain at least two sections:
1. Guest section
 * The regex must contain `(?:_vmr(\\d+))?` at the end of the alias, before the domain.  This ensures that API calls for the dial into the main auditorium will be matched.  It must also contain a group for the unique conference id.  This group must match the conference id group in the host section.
 * `dialout` settings define how this conference will dial into the main auditorium.  The guest VMRS will dial {basename}_{conferenceid}.  The `dialout_basename` must match the beginning og the host conference regex.
 * `participants_per_vmr` defines how many participants will be entered into each VMR before the next VMR is created.

2. Host section
 * Regex must contain a group for the unique conference id, and this must match the group in the guest regex section.

**Sample config**

```
{"configs":
    [
        {
            "alias": "^(?:sip:)?va_([0-9a-zA-Z]{20})(?:_vmr(\\d+))?(?:@<domain>)?$",
            "domain": "<substitute domain name here>",
            "type": "va_guest",
            "basename": "va_",
            "dialout": true,
            "dialout_basename": "vaprov",
            "dialout_location": "<substitute Pexip dialout location here>",
            "dialout_role": "chair",
            "dialout_remote_display_name": "Provider",
            "participants_per_vmr": 4,
            "response": {
                "status": "success",
                "action": "continue",
                "result": {
                    "service_type": "lecture",
                    "name": "va_conference",
                    "service_tag": "va_guest",
                    "max_pixels_per_second": "sd",
                    "enable_overlay_text": true,
                    "host_pin": "2323",
                    "pin": "",
                    "guest_pin": "",
                    "ivr_theme_name": "Large Conference",
                    "guest_view": "one_main_zero_pips",
                    "host_view": "four_mains_zero_pips"
                }
            }
        },
        {
            "alias": "^(?:sip:)?vaprov_([0-9a-zA-Z]{20})(?:@<domain>)?$",
            "domain": "<substitute domain name here>",
            "type": "va_host",
            "basename": "vaprov_",
            "response": {
                "status": "success",
                "action": "continue",
                "result": {
                    "service_type": "lecture",
                    "name": "vaprov_lecture",
                    "allow_guests": true,
                    "service_tag": "va_host",
                    "max_pixels_per_second": "fullhd",
                    "enable_overlay_text": false,
                    "host_pin": "2323",
                    "pin": "2323",
                    "ivr_theme_name": "Large Conference",
                    "guest_view": "one_main_zero_pips",
                    "host_view": "sixteen_mains_zero_pips",
                    "mute_all_guests": true
                }
            }
        }
    ]
}
```
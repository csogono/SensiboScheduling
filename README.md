# SensiboScheduling
Python AWS Lambda function to schedule Sensibo AC events including climate react via IFTTT Webhooks.

FEATURES

* When a climate react condition is met, triggers an IFTTT Webhooks trigger, not the Sensibo API
  directly. Configuring the trigger actions in IFTTT makes it more user friendly.

* Allows multiple climate react schedules.

* Respects the temperature reading age (Sensibo API "secondsAgo"). If the reading age is older than
  the previous poll, then do nothing for that device.

* Respects the state of the AC. If the AC is already ON and the climate react schedule is set to
  switch ON, then do nothing for that device.

* Will only poll the Sensibo API if a schedule is active. If climate react is only active from
  21:00 to 8:00, then no Sensibo API polling will occur from 8:00 to 21:00.


INSTRUCTIONS

This will only work as an AWS Lambda function. With minor changes it could work as a standalone script.
Familiarity with running Python AWS Lambda functions is mandatory. Refer to AWS documentation.

The schedule file defined by the environment variable "ScheduleFilename" must be saved in the same
directory as the Lambda function.

The following environment variables must be set within the Lambda function:
* ScheduleFilename = schedules
* SensiboAPIKey = XXXXXXXXXXXXXXXX
* TempAgeSeconds = 600
* Timezone = Australia/Canberra
* WebhooksAPIKey = YYYYYYYYYYYYY

Ensure that the variables above are properly populated. You will need to generate a Sensibo API Key and
an IFTTT Webhooks API Key. Thee timezone variable is critical and must be set to your local timezone.

After verifying that the function works for you, you will have to schedule a CloudWatch event to
trigger periodic scheduling. The TempAgeSeconds environment value (seconds) must be equal to your
frequency. If you choose 10 minutes then TempAgeSeconds must be 600 seconds.


SCHEDULE CONFIGURATION

A sample schedule configuration file looks like this:

    on,Living,lt,13.5,ac_living,23:45,7:45
    off,Living,gt,25,ac_living_off,0:00,24:00
    on,Bedroom,lt,15,ac_bedroom,21:45,8:00
    on,Study,lt,16,ac_study,8:30,18:00

The columns are as follows:
1. Trigger action mode [on/off] - The trigger action you are trying to achieve
2. Sensibo device name - this is case sensitive
3. Temperature comparison operator [gt/lt] - Operator used to compare the temperature
4. Trigger temperature - Accepts decimals. Only tested in celsius but should work for fahrenheit
5. IFTTT Webhooks trigger - Trigger when the temperature condition is met
6. Schedule start time - Must be 24 hour format such as 21:00
7. Schedule end time - Must be 24 hour format such as 21:00

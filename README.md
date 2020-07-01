# SensiboScheduling
Scheduling of Sensibo AC events including climate react via IFTTT Webhooks

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

The file "schedules" must be saved in the same directory as the Lambda function.

The following environment keys must be set within the Lambda function:
* SensiboAPIKey = XXXXXXXXXXXXXXXX
* TempAgeSeconds = 600
* Timezone = Australia/Canberra
* WebhooksAPIKey = YYYYYYYYYYYYY

Ensure you generate a Sensibo API Key and and IFTTT Webhooks API Key and populate the above
environment values.

Make sure you enter your own timezone!

After verifying that the function works for you, you will have to schedule a CloudWatch event to
trigger periodic scheduling. The TempAgeSeconds environment value (seconds) must be equal to your
frequency. If you choose 10 minutes then TempAgeSeconds must be 600 seconds.

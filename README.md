# About
This project contains a Drozer module, which can be used to send fuzzed Intents to exported components of Android applications automatically. To generate Intents, the fuzzer needs to be fed with information about the expected structure of the Intents' payloads, which the targeted components expect to receive. This can be done via JSON formatted files, like the ones generated by the `StaticAnalyzer` tool. An example file can be seen below:
```json
{
    "com.facebook.lite.TimeSpentLoggingActivity": {
        "intentInvocations": {
            "getStringExtra": ["android.intent.extra.TEXT"],
            "getIntExtra": ["selected_num"],
            "getParcelableExtra": ["output"],
            "getLongExtra": ["uid"],
            "getBooleanExtra": ["camera_result", "result_handled"]
        },
        "bundleInvocations": {
            "getString": ["fb-push-id", "app_growth_upsell_id", "fb-push-json", 
                "identity_graph_device_identifier", "app_growth_impression_id"],
            "getLong": ["fb-push-time"]
        }
    },
    "com.facebook.base.activity.FbFragmentActivity": { ... }
}
```
Furthemore, the fuzzer needs to know all properties specified by Intent filters of the targeted components:
```json
{
    "com.facebook.katana.activity.ImmersiveActivity": {
        "actions": [
            "com.facebook.intent.action.prod.VIEW_NOTIFICATION_SETTINGS",
            "com.facebook.intent.action.prod.VIEW_PERMALINK",
            "com.facebook.intent.action.prod.VIEW_COLLECTION"
        ],
        "categories": ["android.intent.category.DEFAULT"],
        "data": []
    },
    "com.facebook.push.gcmv3.GcmListenerService": { ... }
}
```

# Installation
After cloning this repository to your local file system you can register it to a running Drozer installation. Use the guides provided by Drozer. As soon as the repositoy is registered you can execute the Intent fuzzer via Drozer's `run` command.
```console
$ run intents.fuzzer
```

# Configuration
The fuzzer can be configured via its `config.json` file:
```json
{
    "dataStore": "~/path/to/input/data/files/",
    "outputFolder": "~/output/folder/",
    "androidSDK": "~/Android/Sdk/",
    "intentTimeout": 4,
    "numberIterations": 10,
    "packageNames": ["application.package.names", "which.shall.be.tested"]
}
```

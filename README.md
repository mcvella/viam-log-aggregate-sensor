# log-aggregate modular resource

This module implements the [rdk sensor API](https://github.com/rdk/sensor-api) in a mcvella:sensor:log-aggregate model.
This model aggregates log errors over a specified time period, allowing you to monitor log error counts as well as error counts aggregates by message.

## Build and run

To use this module, follow the instructions to [add a module from the Viam Registry](https://docs.viam.com/registry/configure/#add-a-modular-resource-from-the-viam-registry) and select the `mcvella:sensor:log-aggregate` model from the [`mcvella:sensor:log-aggregate` module](https://app.viam.com/module/rdk/mcvella:sensor:log-aggregate).

## Configure your sensor

> [!NOTE]  
> Before configuring your sensor, you must [create a machine](https://docs.viam.com/manage/fleet/machines/#add-a-new-machine).

Navigate to the **Config** tab of your machine's page in [the Viam app](https://app.viam.com/).
Click on the **Components** subtab and click **Create component**.
Select the `sensor` type, then select the `mcvella:sensor:log-aggregate` model.
Click **Add module**, then enter a name for your sensor and click **Create**.

On the new component panel, copy and paste the following attribute template into your sensor’s **Attributes** box:

```json
{
  "duration_secs": 600
}
```

> [!NOTE]  
> For more information, see [Configure a Machine](https://docs.viam.com/manage/configuration/).

### Attributes

The following attributes are available for `rdk:sensor:mcvella:sensor:log-aggregate` sensors:

| Name | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `duration_secs` | string | Optional |  Duration to track error messages, in seconds.  Default is 600 (10 minutes) |

### Example configuration

```json
{
  "duration_secs": 600
}
```

## Sensor API

The log-aggregate resource implements the [rdk sensor component API](https://github.com/viamrobotics/api/blob/main/proto/viam/component/sensor/v1/sensor.proto).

### get_readings()

get_readings() will return an aggregate total count of log errors over the last [duration_secs](#attributes), as well as a count and details by error message.

Example:

```json
{
  "error_count": 7,
  "errors": {
      {
        "count": 5,
        "file": "eventManager.py:253",
        "last_timestamp": "2024-12-30T17:09:14.891Z",
        "message": "Error in event check loop: (<Status.UNKNOWN: 2>, 'resource \"rdk:service:vision/re_id_S8Fh\" not found', None)",
        "service": "src/eventManager"
      },
      {
        "count": 1,
        "file": "zap/options.go:212",
        "last_timestamp": "2024-12-30T12:08:45.207-0500",
        "message": "finished unary call with code Unknown",
        "service": "rdk.networking"
      },
      {
        "count": 1,
        "file": "rpc/wrtc_server_stream.go:301",
        "last_timestamp": "2024-12-30T17:08:45.207Z",
        "message": "error calling handler",
        "service": "rdk.networking.grpc_requests"
      }
  }
}
```

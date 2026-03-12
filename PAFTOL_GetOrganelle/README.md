# PAFTOL GetOrganelle

## Plastome and ribosome recovery


## Inspect log messages after pipeline runs

The following script extracts WARNING and ERROR messages from GetOrg log files
(transferable to other log files) and saves them as CSVs.

**Outputs**: two CSVs, one with all the warning and errors in the log files
(`warning_error_msgs.csv`) and another with aggregated data by message
(`warning_error_msgs_aggregated.csv`), with a count of the log files where it
appears.

**Usage**

```
python3 GetOrg_log_inspector.py -p /path/to/logs
```

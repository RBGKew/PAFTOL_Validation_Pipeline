#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import pandas as pd


def main():
    args = parse_args()
    base_path = args.logs_base_path.resolve()
    all_messages = get_all_messages(base_path)
    save_msgs_to_csvs(all_messages)
    print("End.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        Get WARNING and ERROR messages from paftol GetOrg log files.
        """
    )
    parser.add_argument(
        "--logs-base-path", "-p",
        type=Path,
        required=True,
        help="Base directory where log files are stored."
    )
    return parser.parse_args()


def get_all_messages(base_path):
    recovery_logs={}
    files = os.listdir(base_path)
    for file in files:
        if file.endswith(".log"):
            file_path=os.path.join(base_path,file)
            recovery_id=get_recovery_id(file_path)
            messages=get_messages_from_recovery_log(file_path)
            recovery_logs[recovery_id]=messages
    return recovery_logs


def get_messages_from_recovery_log(file_path):
    """
    {
      Ornagelle:<pt/nr>
      WARNING:[],
      ERROR:[],
      NumWARNING:<int>,
      NumERROR:<int>
    }
    """
    recovery_id=get_recovery_id(file_path)
    messages={}
    msg_types=["WARNING","ERROR"]
    messages["Organelle"]=recovery_id[-2:]
    try:
        with open(file_path) as f:
            lines = f.readlines()
            for msg_type in msg_types:
                messages[msg_type]=[]
            for line in lines:
                for msg_type in msg_types:
                    if msg_type in line:
                        msg=get_message(line,msg_type)
                        if msg:
                            add_msg_to_messages(messages,msg_type,msg)

        #messages["LogCount"]=1 # to match messages samples data structure
        for msg_type in msg_types:
            messages[f"Num{msg_type}"]=len(messages[msg_type])
        return messages
    except:
        raise


def add_msg_to_messages(msgs_dict,msg_type, msg):
    msgs_dict[msg_type].append(msg)
    return msgs_dict


def get_message(line, msg_type):
    line=line.strip()
    try:
        return line.split(msg_type,1)[1][2:] # removes ": " after ERROR/WARNING
    except:
        return None


def get_recovery_id(path_to_log_file):
    file_name=os.path.basename(path_to_log_file)
    return file_name[4:-4]


def get_messages_aggregated(all_messages):
    aggregated={}
    aggregated_copy=aggregated.copy()
    msg_key=1
    for input_msg in all_messages.values():
        input_msg_copy = input_msg.copy()
        input_msg_copy.pop("LogCount")
        for key, agg_msg in aggregated.items():
            agg_msg_copy=agg_msg.copy()
            agg_msg_copy.pop("LogCount")
            if (input_msg_copy != agg_msg_copy) or not agg_msg:
                aggregated[msg_key]=input_msg
                aggregated[msg_key]["LogCount"]=1
                msg_key+=1
            else:
                aggregated[key]["LogCount"]+=1
    return aggregated


def save_msgs_to_csvs(recovery_logs):
    msgs_table=convert_dict_to_table(recovery_logs)
    aggregated_msgs=aggregate_messages(msgs_table)
    msgs_table.to_csv("warning_error_msgs.csv", index=False)
    aggregated_msgs.to_csv("warning_error_msgs_aggregated.csv", index=False)


def convert_dict_to_table(recovery_logs):
    table = pd.DataFrame.from_dict(recovery_logs, orient="index")
    table.index.name = "RecoveryID"
    table = table.reset_index()
    table["WARNING"] = table["WARNING"].apply(lambda x: " | ".join(x))
    table["ERROR"] = table["ERROR"].apply(lambda x: " | ".join(x))
    return table


def aggregate_messages(recovery_logs_table):
    return (
    recovery_logs_table
    .groupby(["Organelle", "WARNING", "ERROR", "NumWARNING", "NumERROR"])
    .size()
    .reset_index(name="LogCount")
    )


if __name__=="__main__":
    main()

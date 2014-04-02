#!/bin/bash

#   Auth : Tom Lime
#   Date : 01/04/2014
#   Prop : delete snapshots which passed their retention (older than)
#           PLEASE BEWARE: this script rely on snapshot naming convention 
#           to adapt this script following should be done
#           1. IP_NETAPP_NCA/IP_NETAPP_NCB variables updated with proper netapp ip addresses
#           2. VOLUMES_NETAPP_NCA/VOLUMES_NETAPP_NCB variables updated with volume names


BIN_RSH=/usr/bin/rsh
#------- config section ------#
IP_NETAPP_NCA=10.0.0.1
IP_NETAPP_NCB=10.0.0.2
VOLUMES_NETAPP_NCA=(vol_prod_part_001
                    vol_prod_part_002)
VOLUMES_NETAPP_NCB=(vol_prod_part_003)
#----------- end -------------#


function usage {
    echo "Usage: $0 SNAP_TYPE [RETENTION]"
    echo "    SNAP_TYPE - hourly, daily, weekly"
    echo "    RETENTION - must be in days"
    echo "    Example: $0 daily 14"
    exit 1
}


function snap_time_to_epoch {
    # convert timestamp of following format YYYYmmddHHDDSS to epoch seconds 
    local _SNAP_TIME=$1
    local _TIMESTAMP=${_SNAP_TIME:0:12}
    local _DATE=${_TIMESTAMP:0:8}
    local _TIME=${_TIMESTAMP:8:12}
    local _EPOCH=$(date -d "$_DATE $_TIME" +%s)

    echo $_EPOCH
} 


function get_snapshots {
    # get a list of snapshots and return in reverse order (last snapshot goes first)
    local _NETAPP_IP=$1
    local _VOL_NAME=$2
    #hourly,daily,weekly
    local _SNAP_TYPE=$3
    # example vol_prod_part_001_Snap-daily_20140401175500
    local _PATTERN="^vol_prod_part_[0-9]+_Snap-${_SNAP_TYPE}_[0-9]+.$"
    local _SNAPSHOTS=$(${BIN_RSH} ${_NETAPP_IP} "snap list -b ${_VOL_NAME}" | grep -E "${_PATTERN}")

    echo $_SNAPSHOTS | sort -r
}


function get_snapshot_timestamp {
    # extract timestamp from snapshot name
    local _SNAP_NAME=$1
    local _TIMESTAMP=$(echo ${_SNAP_NAME} | grep -Eo "[0-9]+.$")

    echo $_TIMESTAMP
}


function delete_snapshot {
    # delete snapshot forever >:^)
    local _NETAPP_IP=$1
    local _VOL_NAME=$2
    local _SNAP_NAME=$3
    echo "[INFO]: Deleting snapshot: ${_NETAPP_IP} ${_VOL_NAME} ${_SNAP_NAME}"
    #FIXME: remove this execution guard
    #echo $BIN_RSH ${_NETAPP_IP} "snap delete ${_VOL_NAME} ${_SNAP_NAME}"; local _RC=$?

    return $_RC
}


#
# main
#

# passing and checking params
OPT_SNAP_TYPE=$1
OPT_RETENTION=$2
if [[ ! "$OPT_SNAP_TYPE" =~ ^hourly|daily|weekly$ ]]; then
    usage
fi
if [[ -z "$OPT_RETENTION" ]]; then
    # supply default retention params;based on snap retention policy from 01/04/2014
    case "$OPT_SNAP_TYPE" in 
        hourly) OPT_RETENTION=1;;
        daily) OPT_RETENTION=14;;
        weekly) OPT_RETENTION=7;;
        *) usage;;
    esac
fi
if [[ ! "$OPT_RETENTION" =~ ^[0-9]{1,3}$ ]]; then
    usage
fi

echo "[INFO]: Started ..."
# convert OPT_RETENTION days to seconds
RETENTION_SECS=$((60 * 60 * 24 * ${OPT_RETENTION}))
# obtain snapshot list of first volume in VOLUMES_NETAPP_NCB array 
SNAP_LIST=($(get_snapshots $IP_NETAPP_NCB ${VOLUMES_NETAPP_NCB[@]:0:1} ${OPT_SNAP_TYPE}))
# obtain last snapshot taken
SNAP_LAST=${SNAP_LIST[*]:0:1}
# extract timestamp from snapshot name
SNAP_LAST_TS=$(get_snapshot_timestamp ${SNAP_LAST})
# convert timestamp to epoch seconds
SNAP_LAST_EP=$(snap_time_to_epoch ${SNAP_LAST_TS})

# array to store snapshots which should be deleted
SNAP_DEL_LIST=()
for snap in ${SNAP_LIST[@]}; do
    snap_ts=$(get_snapshot_timestamp ${snap})
    snap_ep=$(snap_time_to_epoch ${snap_ts})
    # consider snapshot to deleted if last_snapshot_epoch_seconds_value greater than checked_snapshot_epoch_seconds + retention_seconds
    if [[ "${SNAP_LAST_EP}" -gt "$((${snap_ep} + ${RETENTION_SECS}))" ]]; then
        echo "[WARNING]: Violated retention of ${OPT_RETENTION} -> $snap"
        SNAP_DEL_LIST+=(${snap})
    fi
done

if [[ -z "${SNAP_DEL_LIST}" ]]; then
    # if nothing to delete just let the user know
    echo "[INFO]: Nothing to delete ..."
else 
    # otherwise start to delete snapshots
    for volume in ${VOLUMES_NETAPP_NCA[@]}; do
        for snap in ${SNAP_DEL_LIST[@]}; do
            delete_snapshot ${IP_NETAPP_NCA} ${volume} ${snap}
        done
    done
    for volume in ${VOLUMES_NETAPP_NCB[@]}; do
        for snap in ${SNAP_DEL_LIST[@]}; do
            delete_snapshot ${IP_NETAPP_NCB} ${volume} ${snap}
        done
    done
fi

echo "[INFO]: Finished ..."
exit 0

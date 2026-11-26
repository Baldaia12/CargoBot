# Usar source ambiente.bash em cada terminal.
trc_raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source /opt/ros/jazzy/setup.bash || return 1
if [[ -f "$trc_raiz/install/local_setup.bash" ]]; then
    source "$trc_raiz/install/local_setup.bash" || return 1
fi
export ROS_DOMAIN_ID="${TRC_DOMAIN_ID:-42}"
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_AUTOMATIC_DISCOVERY_RANGE=SYSTEM_DEFAULT
export GZ_PARTITION="trc_mapping_${ROS_DOMAIN_ID}"
unset trc_raiz

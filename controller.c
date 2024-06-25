#include "header.h"
//Definition of control modules
float speed_control(float speed, float ref){
    return (ref-speed)*3;
}

//Main control input "packer"
data_outgoing_type main_controller(data_incoming_type outputs){
    data_outgoing_type inputs;
    inputs.force=speed_control(outputs.Vx,outputs.Vx_ref);
    return inputs;
}
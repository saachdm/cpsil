#include "header.h"

float prop_input,brake_input;

//Definition of control modules
void speed_control(float vx, float vx_ref, float* prop_input, float* brake_input){
    float tol=0.1;
    if(vx_ref-vx>tol){ //Speed increase requested
        *prop_input=(vx_ref-vx)*3;
        *brake_input=0;
    } else if(vx_ref-vx<0){ //Speed decrease requested
        *prop_input=0;
        *brake_input=(vx-vx_ref)*3;
    }else{  //Speed increase requested (but within {tol})
        *prop_input=(vx_ref-vx)*1.5;
        *brake_input=0;
    };
}

//Main control input "packer"
data_outgoing_type main_controller(data_incoming_type outputs){
    data_outgoing_type inputs;
    speed_control(outputs.Vx,outputs.Vx_ref,&prop_input,&brake_input);
    printf("Prop_input: %f \n",prop_input);
    inputs.prop_input=prop_input;
    inputs.brake_input=brake_input;
    return inputs;
}
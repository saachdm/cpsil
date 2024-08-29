#include "header.h"

// "input" in this scope is defined as the input **to** the vehicle
// "output" in this scope is defined as the output **coming from** the vehicle

// Define the "inputs". This corresponds to the 
float prop_input,brake_input;
int gear_input; 

//Definition of control modules
//The control modules basically receive the "outputs" and modify the "inputs" values

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

// Simple speed-based automatic gear (speeds are in m/s)
void gear_control(float vx, int *gear_input) {
    if (vx > 16.6) {
        *gear_input = 5;
    } else if (vx > 12.5) {
        *gear_input = 4;
    } else if (vx > 8.3) {
        *gear_input = 3;
    } else if (vx > 4.16) {
        *gear_input = 2;  
    } else {
        *gear_input = 1; 
    }
}


//Main control input "packer"
data_outgoing_type main_controller(data_incoming_type outputs){
    data_outgoing_type inputs;

    //Control modules
    speed_control(outputs.Vx,outputs.Vx_ref,&prop_input,&brake_input);
    gear_control(outputs.Vx,&gear_input);
    //Input packing
    inputs.prop_input=prop_input;
    inputs.brake_input=brake_input;
    inputs.gear_input=gear_input;
    return inputs;
}
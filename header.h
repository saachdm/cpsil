#ifndef HEADER
#define HEADER
typedef struct data_outgoing{
    float prop_input;
    float brake_input;
} data_outgoing_type;

typedef struct data_incoming{
    float Vx;
    float Vx_ref;
} data_incoming_type;

// typedef struct data_incoming_mode{
//     float yyyy;
//     float zzzz;
// } data_incoming_mode_type;

#endif
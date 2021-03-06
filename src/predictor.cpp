#include <ArduinoBLE.h>
#include <string>

#include "TensorFlowLite.h"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"
#include "arm_lite_model.h"
#include "hip_lite_model.h"
#include "ble.h"

#define DEBUG 1

int direction = 0;
int debounce = 0;
int last_direction = 0;
String predict;
const char* activity[9] = {"si", "sc", "st", "pr", "wa", "ru", "sj", "pu", "pl"};

// TFLite globals, used for compatibility with Arduino-style sketches
namespace
{
    tflite::ErrorReporter *error_reporter = nullptr;
    const tflite::Model *model = nullptr;
    tflite::MicroInterpreter *interpreter = nullptr;
    TfLiteTensor *model_input = nullptr;
    TfLiteTensor *model_output = nullptr;

    // Create an area of memory to use for input, output, and other TensorFlow
    // arrays. You'll need to adjust this by combiling, running, and looking
    // for errors.
    constexpr int kTensorArenaSize = 20 * 1024;
    byte tensor_arena[kTensorArenaSize] __attribute__((aligned(16)));

}

void init_predictor()
{
    static tflite::MicroErrorReporter micro_error_reporter;
    error_reporter = &micro_error_reporter;
    tflite::AllOpsResolver resolver;
    // Map the model into a usable data structure
    model = tflite::GetModel(arm_lite_model);
    

    if (model->version() != TFLITE_SCHEMA_VERSION)
    {
        error_reporter->Report("Model version does not match Schema");
        while (1)
        {

        }
    }

    static tflite::MicroMutableOpResolver<8> micro_op_resolver;  // NOLINT
    micro_op_resolver.AddConv2D();
    micro_op_resolver.AddMean();
    micro_op_resolver.AddFullyConnected();
    micro_op_resolver.AddSoftmax();
    micro_op_resolver.AddStridedSlice();
    micro_op_resolver.AddTanh();
    micro_op_resolver.AddDepthwiseConv2D();
    micro_op_resolver.AddMaxPool2D();

    // Build an interpreter to run the model
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize,
        error_reporter);
    interpreter = &static_interpreter;
    
    // Allocate memory from the tensor_arena for the model's tensors
    TfLiteStatus allocate_status = interpreter->AllocateTensors();

    if (allocate_status != kTfLiteOk)
    {
        error_reporter->Report("AllocateTensors() failed");
        while (1)
        {
            Serial.println("ALLOCATE FAIL");
        }
    }

    // Assign model input and output buffers (tensors) to pointers
    model_input = interpreter->input(0);
    model_output = interpreter->output(0);

#if DEBUG
    Serial.print("Number of dimensions: ");
    Serial.println(model_input->dims->size);
    Serial.print("Dim 1 size: ");
    Serial.println(model_input->dims->data[0]);
    Serial.print("Dim 2 size: ");
    Serial.println(model_input->dims->data[1]);
    Serial.print("Input type: ");
    Serial.println(model_input->type);
#endif
}

String predictor(float x, float y, float z)
{

    model_input->data.f[0] = x;
    model_input->data.f[1] = y;
    model_input->data.f[2] = z;

    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk)
    {
        error_reporter->Report("Invoke failed on input: %f, %f, %f\n", x, y, z);
    }

    int maximum = model_output->data.f[0];

    for (int i = 1; i < 9; i++)
    {
        if (model_output->data.f[i] >= maximum)
        {
            maximum = model_output->data.f[i];
            direction = i;
        }
    }

    Serial.println(direction);

    if (last_direction == direction)
    {
        debounce++;
    }

    if (debounce > 0)
    {
        if (direction == 0)
        {
            predict = "SIT";
        }
        else if (direction == 1)
        {
            predict = "SITCROSS";
        }
        else if (direction == 2)
        {
            predict = "STAND";
        }
        else if (direction == 3)
        {
            predict = "PRONE";
        }
        else if (direction == 4)
        {
            predict = "WALK";
        }
        else if (direction == 5)
        {
            predict = "RUN";
        }
        else if (direction == 6)
        {
            predict = "STARJUMP";
        }
        else if (direction == 7)
        {
            predict = "PUSHUP";
        }
        else if (direction == 8)
        {
            predict = "PLANK";
        }
        debounce = 0;
    }
    last_direction = direction;
    for(int i = 0; i < 9; i++) 
    {
        String softmax = " ";
        softmax.concat(model_output->data.f[i]);
        softmax = activity[i] + softmax;
        tx_ble_message(softmax);
    }
    
    return predict;
}


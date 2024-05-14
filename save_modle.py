import tensorflow as tf
import tensorflow_hub as hub

# Load the TensorFlow Hub model
hub_model = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")

# Convert the model to concrete function
concrete_func = hub_model.signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
concrete_func.inputs[0].set_shape([1, 300, 300, 3])

# Convert the model to a TensorFlow Lite model
converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
tflite_model = converter.convert()

# Save the TensorFlow Lite model
with open('test_modle/model.tflite', 'wb') as f:
    f.write(tflite_model)
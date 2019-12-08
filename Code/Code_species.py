import sys

print(sys.argv[1])

enum = int(sys.argv[1])


#Divisão do Conjunto de Imagem
import split_folders

#Bibliotecas empregadas na análise
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping


#model
img_width, img_height = 299, 299
train_data_dir = "../data/pollen23e_split_multi/train"
validation_data_dir = "../data/pollen23e_split_multi/val"

#data_generate
seed = 42

per_train = 0.6
per_test = 0.2 
per_validation = 0.2
seed_split_folder = 42

split_folders.ratio(input='../data/pollen23e/', 
                    output="../data/pollen23e_split", 
                    seed=seed_split_folder, 
                    ratio=(per_train, per_test, per_validation)) # default values


lr=1E-3
momentum= 0.9
batch_size = 64
epochs = 30

train_datagen = ImageDataGenerator(
           rotation_range=45,
           width_shift_range=0.1,
           height_shift_range=0.1,
           shear_range=0.01,
           zoom_range=[0.9,1.25],
           horizontal_flip=True,
           vertical_flip=True,
           fill_mode='reflect',
           data_format='channels_last',
           brightness_range=[0.5, 1.5])

test_datagen = ImageDataGenerator()


from tensorflow.keras.applications import DenseNet121, DenseNet169, DenseNet201, InceptionResNetV2, InceptionV3, MobileNet, MobileNetV2, NASNetMobile, ResNet101, ResNet101V2, ResNet152, ResNet152V2, ResNet50, ResNet50V2, VGG16, VGG19, Xception

from tensorflow.keras.layers import Dense

models       = [DenseNet121, DenseNet169, DenseNet201, 
                InceptionResNetV2, InceptionV3, MobileNet, 
                MobileNetV2,  NASNetMobile, 
                ResNet101, ResNet101V2, ResNet152, 
                ResNet152V2, ResNet50, ResNet50V2, 
                VGG16, VGG19, Xception]

models_name =  ['DenseNet121','DenseNet169','DenseNet201',
                'InceptionResNetV2','InceptionV3','MobileNet',
                'MobileNetV2','NASNetMobile',
                'ResNet101','ResNet101V2','ResNet152',
                'ResNet152V2','ResNet50','ResNet50V2',
                'VGG16','VGG19','Xception']


img_width, img_height =  299, 299



train_generator = train_datagen.flow_from_directory(
                        '../data/pollen23e_split/train',
                        target_size = (299,299),
                        batch_size = batch_size,
                        save_to_dir = '../data/pollen23e_aug/train',
                        save_prefix='aug', 
                        save_format='png',
                        class_mode = "categorical",
                        follow_links = True,
                        seed = seed)

validation_generator = train_datagen.flow_from_directory(
                        '../data/pollen23e_split/val',
                        target_size = (299,299),
                        batch_size = batch_size,
                        class_mode = "categorical",
                        save_to_dir = '../data/pollen23e_aug/valid',
                        save_prefix='aug', 
                        save_format='png',
                        follow_links = True,
                        seed = seed)

test_generator = test_datagen.flow_from_directory(
                        '../data/pollen23e_split/test',
                        target_size = (299,299),
                        batch_size = batch_size,
                        class_mode = 'categorical',
                        follow_links = True,
                        seed = seed)



# Save the model according to the conditions
checkpoint = ModelCheckpoint("../checkpoints/"+models_name[enum], 
                             monitor='val_loss', verbose=1, 
                             save_weights_only=False, 
                             mode='auto', save_freq='epoch', 
                             save_best_only=True)

model = models[enum](weights     = "imagenet", 
                     include_top = False, 
                     input_shape = (img_width, img_height, 3))

#Adicionando um camada adicional
x = model.output
x = Flatten()(x)
predictions = Dense(23, activation="softmax",use_bias=False)(x)

# Camada final
model = Model(model.input,predictions)
# compile the model
model.compile(loss = "categorical_crossentropy", 
              optimizer =  optimizers.SGD(lr=lr, momentum=momentum),
              metrics=["accuracy"])


history_acc = model.fit_generator(
            train_generator,
            steps_per_epoch = train_generator.samples/batch_size,
            epochs = epochs,
            callbacks = [checkpoint],
            validation_data = validation_generator,
            validation_steps = validation_generator.samples/batch_size)

model.save("../checkpoints/"+models_name[enum]+".h5")    



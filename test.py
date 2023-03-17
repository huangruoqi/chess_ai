import os
def get_new_models():
    os.system("git pull origin main")
    training_instances = os.listdir('saved_model')
    candidates = []
    for i in training_instances:
        # if i==LETTER: continue
        instance_path = os.path.join('saved_model', i)
        model_names = os.listdir(instance_path)
        model_names.sort(reverse=True)
        print(model_names[:10])
        for j in model_names:
            model_path = os.path.join(instance_path, j) 
            with open(os.path.join(model_path, 'info.txt'), 'r') as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))

get_new_models()
import detect_compo.ip_region_proposal as ip

key_params = {'min-grad': 10, 'ffl-block': 5, 'min-ele-area': 50, 'merge-contained-ele': True,
              'max-word-inline-gap': 4, 'max-line-gap': 4}

input_path_img = 'data/input/1.jpg'
output_root = 'data/output'

ip.compo_detection(input_path_img, output_root, key_params, resize_by_height=None, show=True)

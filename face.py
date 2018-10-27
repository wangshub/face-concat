import argparse
import math
from PIL import Image, ImageDraw
import face_recognition


def get_parser():
    """
    parse command line args
    :return:
    """
    parser = argparse.ArgumentParser(description='face cut & concat tool')
    parser.add_argument('-l', '--left', type=str, help='face on the left')
    parser.add_argument('-r', '--right', type=str, help='face on the right')
    parser.add_argument('-u', '--upside', type=str, help='face on the upside')
    parser.add_argument('-d', '--downside', type=str, help='face on the downside')
    args = vars(parser.parse_args())
    return args


def midpoint(coors):
    """
    get midpoint of coors
    :param coors:[(x, y), ...]
    :return:
    """
    x, y = 0, 0
    for coor in coors:
        x += coor[0]
        y += coor[1]
    x, y = int(x / len(coors)), int(y / len(coors))
    return x, y


def distance(coor0, coor1):
    d = (coor0[0] - coor1[0])**2 + (coor0[1] - coor1[1])**2
    d = math.sqrt(d)
    return d


def load_image(image_file):
    """
    Load the jpg file into a numpy array
    :param image_file:
    :return:
    """
    image_array = face_recognition.load_image_file(image_file)
    return image_array


def get_facial_landmark(image_array):
    """
     Find all facial features in all the faces in the image
    :param image_array:
    :return:
    """
    landmarks_list = face_recognition.face_landmarks(image_array)
    return landmarks_list


def cut_half_face(image_path, retain_side):
    """
    retain the desired side of image
    :param image:
    :param retain_side:
    :return:
    """
    image = load_image(image_path)
    landmark = get_facial_landmark(image)[0]
    nose_bridge_midpoint = midpoint(landmark['nose_bridge'])
    # print(landmark.keys())
    print('nose_bridge_midpoint =', nose_bridge_midpoint, image_path)
    pil_image = Image.fromarray(image)
    image_size = pil_image.size
    print('image_size = ', image_size, image_path)

    location_points = None
    half_image = None

    if retain_side == 'left':
        location_points = [(nose_bridge_midpoint[0], midpoint(landmark['left_eyebrow'])[1]),
                           (nose_bridge_midpoint[0], midpoint(landmark['top_lip'])[1])]
        crop_area = (0, 0) + (nose_bridge_midpoint[0], image_size[1])
        half_image = pil_image.crop(crop_area)
    elif retain_side == 'right':
        location_points = [(0, midpoint(landmark['left_eyebrow'])[1]),
                           (0, midpoint(landmark['top_lip'])[1])]
        crop_area = (nose_bridge_midpoint[0], 0) + image_size
        half_image = pil_image.crop(crop_area)
    elif retain_side == 'upside':
        # TODO
        pass
    elif retain_side == 'downside':
        # TODO
        pass
    else:
        pass

    return half_image, location_points


def concat_horizontal(image_left_path, image_right_path):
    image_left, loc_left = cut_half_face(image_left_path, 'left')
    image_right, loc_right = cut_half_face(image_right_path, 'right')
    scale_ratio = distance(loc_left[0], loc_left[1]) / distance(loc_right[0], loc_right[1])

    print('scale_ratio = ', scale_ratio)

    if scale_ratio > 1:
        to_size = tuple([int(item / scale_ratio) for item in image_left.size])
        image_left = image_left.resize(to_size, Image.ANTIALIAS)
        loc_left = [(int(item[0] / scale_ratio), int(item[1] / scale_ratio)) for item in loc_left]
    else:
        to_size = tuple([int(item * scale_ratio) for item in image_right.size])
        image_right = image_right.resize(to_size, Image.ANTIALIAS)
        loc_right = [(int(item[0] * scale_ratio), int(item[1] * scale_ratio)) for item in loc_right]
    # image_left.show()
    # image_right.show()
    print('loc_left, loc_right = ', loc_left, loc_right)
    print('image_left.size, image_right.size = ', image_left.size, image_right.size)
    w_l, h_l = image_left.size
    w_r, h_r = image_right.size

    # area cut
    hl, hr = loc_left[0][1], loc_right[0][1]
    y_l_0, y_r_0 = (hl, hr - hl) if hl < hr else (hl - hr, hr)

    hl, hr = (h_l - loc_left[1][1]), (h_r - loc_right[1][1])
    delta = hl - hr
    y_l_1, y_r_1 = (loc_left[1][1], loc_right[1][1] + delta) if delta < 0 else (loc_left[1][1] - delta, loc_right[1][1])

    crop_area_l = (0, y_l_0, w_l, y_l_1)
    crop_area_r = (0, y_r_0, w_r, y_r_1)

    print(crop_area_l, crop_area_r)

    crop_image_l = image_left.crop(crop_area_l)
    crop_image_r = image_right.crop(crop_area_r)

    # crop_image_l.show()
    # crop_image_r.show()




def concat_vertical(images):
    pass


def test():
    image = load_image("face/trump-1.jpg")

    face_landmarks_list = get_facial_landmark(image)
    print("I found {} face(s) in this photograph.".format(len(face_landmarks_list)))
    num_faces = len(face_landmarks_list)

    if num_faces == 1:
        # Create a PIL imagedraw object so we can draw on the picture
        pil_image = Image.fromarray(image)
        img_size = pil_image.size
        d = ImageDraw.Draw(pil_image)

        for face_landmarks in face_landmarks_list:
            for facial_feature in face_landmarks.keys():
                print("{} : {}".format(facial_feature, face_landmarks[facial_feature]))

        face_landmarks = face_landmarks_list[0]
        centre_nose_bridge = midpoint(face_landmarks['nose_bridge'])

        d.point(centre_nose_bridge, fill='yellow')
        pil_image.show()

    else:
        print('multi face not support or empty face')

    # Show the picture
    # pil_image.show()

    # area = (400, 400, 800, 800)
    # cropped_img = pil_image.crop(area)
    # cropped_img.show()


def main():
    args = get_parser()
    print(args)

    if args['left'] and args['right']:
        concat_horizontal(args['left'], args['right'])

    if args['upside'] and args['downside']:
        # TODO
        pass



if __name__ == '__main__':
    main()
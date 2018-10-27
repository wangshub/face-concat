import argparse
import math
from PIL import Image, ImageDraw
import face_recognition
from functools import reduce


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
    parser.add_argument('-o', '--output', type=str, help='save concat file')

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


def lowest_point(coors):
    """
    find the lowest coor in coors
    :param coors:
    :return:
    """
    lowest_coor = reduce(lambda x, y: x if x[1] > y[1] else y, coors)
    return lowest_coor


def intersection(start, coors):
    """
    get nose tip to chin intersection
    :param start:
    :param coors:
    :return:
    """
    coors_l = [i for i in coors if i[0] < start[0]]
    intersection_l = reduce(lambda a, b: a if abs(a[1] - start[1]) < abs(b[1] - start[1]) else b, coors_l)
    coors_r = [i for i in coors if i[0] > start[0]]
    intersection_r = reduce(lambda a, b: a if abs(a[1] - start[1]) < abs(b[1] - start[1]) else b, coors_r)
    return intersection_l, intersection_r


def distance(coor0, coor1):
    d = (coor0[0] - coor1[0]) ** 2 + (coor0[1] - coor1[1]) ** 2
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
    # print(landmark)
    print('nose_bridge_midpoint =', nose_bridge_midpoint, image_path)
    pil_image = Image.fromarray(image)
    image_size = pil_image.size
    print(image_path, 'image_size = ', image_size)

    location_points = None
    half_image = None

    if retain_side == 'left':
        location_points = [(nose_bridge_midpoint[0], midpoint(landmark['left_eye'])[1]),
                           (nose_bridge_midpoint[0], midpoint(landmark['top_lip'])[1])]
        crop_area = (0, 0) + (nose_bridge_midpoint[0], image_size[1])
        half_image = pil_image.crop(crop_area)
    elif retain_side == 'right':
        location_points = [(0, midpoint(landmark['right_eye'])[1]),
                           (0, midpoint(landmark['top_lip'])[1])]
        crop_area = (nose_bridge_midpoint[0], 0) + image_size
        half_image = pil_image.crop(crop_area)
    elif retain_side == 'upside':
        # TODO
        nose_tip = lowest_point(landmark['nose_tip'])
        loc_left, loc_right = intersection(nose_tip, landmark['chin'])
        location_points = [loc_left, loc_right]
        crop_area = (0, 0) + (image_size[0], nose_tip[1])
        half_image = pil_image.crop(crop_area)
    elif retain_side == 'downside':
        # TODO
        nose_tip = lowest_point(landmark['nose_tip'])
        loc_left, loc_right = intersection(nose_tip, landmark['chin'])
        location_points = [(loc_left[0], 0), (loc_right[0], 0)]
        crop_area = (0, nose_tip[1]) + image_size
        half_image = pil_image.crop(crop_area)
    else:
        pass

    return half_image, location_points


def concat_horizontal(image_left_path, image_right_path, concat_path):
    image_left, loc_left = cut_half_face(image_left_path, 'left')
    image_right, loc_right = cut_half_face(image_right_path, 'right')
    scale_ratio = distance(loc_left[0], loc_left[1]) / distance(loc_right[0], loc_right[1])

    if scale_ratio > 1:
        to_size = tuple([int(item / scale_ratio) for item in image_left.size])
        image_left = image_left.resize(to_size, Image.ANTIALIAS)
        loc_left = [(int(item[0] / scale_ratio), int(item[1] / scale_ratio)) for item in loc_left]
    else:
        to_size = tuple([int(item * scale_ratio) for item in image_right.size])
        image_right = image_right.resize(to_size, Image.ANTIALIAS)
        loc_right = [(int(item[0] * scale_ratio), int(item[1] * scale_ratio)) for item in loc_right]

    wl, hl = image_left.size
    wr, hr = image_right.size

    delta = loc_left[0][1] - loc_right[0][1]
    yl_0, yr_0 = (delta, 0) if delta > 0 else (0, -delta)

    delta = (hl - loc_left[1][1]) - (hr - loc_right[1][1])
    yl_1, yr_1 = (hl - delta, hr) if delta > 0 else (hl, hr + delta)
    area_l = (0, yl_0, wl, yl_1)
    area_r = (0, yr_0, wr, yr_1)
    image_crop_l = image_left.crop(area_l)
    image_crop_r = image_right.crop(area_r)

    new_im = Image.new('RGB', (wl + wr, image_crop_l.size[1]))
    new_im.paste(image_crop_l, (0, 0))
    new_im.paste(image_crop_r, (wl, 0))
    # new_im.show()
    new_im.save(concat_path)


def concat_vertical(image_up_path, image_down_path, concat_path):
    image_up, loc_up = cut_half_face(image_up_path, 'upside')
    image_dw, loc_dw = cut_half_face(image_down_path, 'downside')
    scale_ratio = (loc_up[1][0] - loc_up[0][0]) / (loc_dw[1][0] - loc_dw[0][0])
    print('scale_ratio = ', scale_ratio)
    if scale_ratio > 1:
        to_size = tuple([int(item / scale_ratio) for item in image_up.size])
        image_up = image_up.resize(to_size, Image.ANTIALIAS)
        loc_up = [(int(item[0] / scale_ratio), int(item[1] / scale_ratio)) for item in loc_up]
    else:
        to_size = tuple([int(item * scale_ratio) for item in image_dw.size])
        image_dw = image_dw.resize(to_size, Image.ANTIALIAS)
        loc_dw = [(int(item[0] * scale_ratio), int(item[1] / scale_ratio)) for item in loc_dw]
    # image_up.show()
    # image_dw.show()
    print('loc_up, loc_dw = ', loc_up, loc_dw)
    w_up, h_up = image_up.size
    w_dw, h_dw = image_dw.size
    delta = loc_up[0][0] - loc_dw[0][0]
    x_up0, x_dw0 = (delta, 0) if delta > 0 else (0, -delta)

    delta = (w_up - loc_up[1][0]) - (w_dw - loc_dw[1][0])
    x_up1, x_dw1 = (w_up - delta, w_dw) if delta > 0 else (w_up, w_dw + delta)

    area_up = (x_up0, 0, x_up1, h_up)
    area_dw = (x_dw0, 0, x_dw1, h_dw)
    image_crop_up = image_up.crop(area_up)
    image_crop_dw = image_dw.crop(area_dw)
    # image_crop_up.show()
    # image_crop_dw.show()
    new_im = Image.new('RGB', (image_crop_up.size[0], h_up + h_dw))
    new_im.paste(image_crop_up, (0, 0))
    new_im.paste(image_crop_dw, (0, h_up))
    # new_im.show()
    new_im.save(concat_path)


def main():
    args = get_parser()
    if args['left'] and args['right'] and args['output']:
        concat_horizontal(args['left'], args['right'], args['output'])

    if args['upside'] and args['downside'] and args['output']:
        concat_vertical(args['upside'], args['downside'], args['output'])


if __name__ == '__main__':
    main()

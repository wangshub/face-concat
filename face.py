import argparse
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


if __name__ == '__main__':
    args = get_parser()
    print(args)
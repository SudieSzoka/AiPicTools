from PIL import Image,ImageDraw
import os

# 中景透明度
mid_transparency = 0.5

# 圆角像素
mid_rounded_rectangle = 30
pre_rounded_rectangle = 15

mid_edge_x,mid_edge_y = 20,20
back_edge_x,back_edge_y = 20,20
# 边缘占图片比例最少
edge_ratio = 0.03
# 定义渐变色方案
grad_colors = [
    [(214, 233, 255), (214, 229, 255), (209, 214, 255), (221, 209, 255), (243, 209, 255), (255, 204, 245), (255, 204, 223), (255, 200, 199), (255, 216, 199), (255, 221, 199)],
    [(204, 251, 252), (197, 234, 254), (189, 211, 255)],
    [(255, 242, 158), (255, 239, 153), (255, 231, 140), (255, 217, 121), (255, 197, 98), (255, 171, 75), (255, 143, 52), (255, 115, 33), (255, 95, 20), (255, 87, 15)],
    [(211, 89, 255), (228, 99, 255), (255, 123, 247), (255, 154, 218), (255, 185, 208), (255, 209, 214), (255, 219, 219)],
    [(0, 224, 245), (31, 158, 255), (51, 85, 255)],
    [(255, 25, 125), (45, 13, 255), (0, 255, 179)],
    [(0, 176, 158), (19, 77, 93), (16, 23, 31)],
    [(95, 108, 138), (48, 59, 94), (14, 18, 38)]
]

# 绘制圆角矩形
def crop_to_rounded_rectangle(image, corner_radius):
    # 打开原始图片
    # image = Image.open(image_path).convert("RGBA")

    # 创建一个空白的遮罩图像，与原始图片尺寸一致
    mask = Image.new("L", image.size, 0)

    # 创建一个可绘制对象
    draw = ImageDraw.Draw(mask)

    # 绘制圆角矩形区域为白色（255）
    x0, y0 = 0, 0
    x1, y1 = image.width, image.height
    draw.rounded_rectangle([(x0, y0), (x1, y1)], corner_radius, fill=255)

    # 创建一个空白的 RGBA 图像，与原始图片尺寸一致
    output_image = Image.new("RGBA", image.size)

    # 在输出图像上绘制圆角矩形区域，并将原始图片通过遮罩应用到输出图像上
    output_image.paste(image, (0, 0), mask=mask)

    return output_image

def transparentize_image(image, transparency,mid_w,mid_h,back_extra_x,back_extra_y):
	# 创建一个空白图片
	image_white = Image.new("RGBA", (mid_w,mid_h), (255, 255, 255, 255))
	image_white = crop_to_rounded_rectangle(image_white, mid_rounded_rectangle)
	# 裁剪图片
	cropped_image = image.crop((back_extra_x, back_extra_y, back_extra_x+mid_w, back_extra_y+mid_h))
	cropped_image = crop_to_rounded_rectangle(cropped_image, mid_rounded_rectangle)
	blended_image = Image.blend(cropped_image, image_white, transparency)
	
	image.paste(blended_image,(back_extra_x,back_extra_y),blended_image)
	
	return image

def main(img_path,grad_index):
    # 选定渐变方案序号，范围：0~7
    i = grad_index 
    grad = grad_colors[i]

    file_name = img_path
    if file_name.endswith('png'):
        img_pre = Image.open(file_name)
    else:
        img_pre = Image.open(file_name).convert("RGBA")
    # 获取文件的基本名（不包括扩展名）
    base_name = os.path.basename(file_name).rsplit(".", 1)[0]

    pre_w,pre_h = img_pre.size

    mid_extra_x = min(mid_edge_x,int(edge_ratio*pre_w))
    mid_extra_y = min(mid_edge_y,int(edge_ratio*pre_h))
    mid_w,mid_h = pre_w + mid_extra_x*2 ,pre_h + mid_extra_y*2

    back_extra_x = min(back_edge_x,int(edge_ratio*pre_w))
    back_extra_y = min(back_edge_y,int(edge_ratio*pre_h))
    back_w,back_h = mid_w + back_extra_x*2 ,mid_h + back_extra_y*2

    # 创建背景区域
    image = Image.new("RGBA", (back_w,back_h))
    draw = ImageDraw.Draw(image)

    # 绘制渐变色矩形
    color_num = len(grad)
    list_color_step = []
    for j in range(color_num-1):
        r_step = (grad[j+1][0] - grad[j][0])
        g_step = (grad[j+1][1] - grad[j][1])
        b_step = (grad[j+1][2] - grad[j][2])
        list_color_step.append([r_step,g_step,b_step])

    for h in range(back_h):
        percent = h/back_h*(color_num-1)
        index = int(percent)
        ratio = percent % 1
        color = (
            int(grad[index][0] + list_color_step[index][0] * ratio),
            int(grad[index][1] + list_color_step[index][1] * ratio),
            int(grad[index][2] + list_color_step[index][2] * ratio)
        )

        draw.rectangle([(0, h), (back_w, h)], fill=color)
    # 调用函数进行透明化处理（例子中透明度为0.5）
    new_img = image
    # new_img = transparentize_image(image, mid_transparency,mid_w,mid_h,back_extra_x,back_extra_y)
    # 前景图本来需要切圆角。由于双重圆角不好看，且加了透明度后更不好看。因此取消
    # img_pre_rounded = crop_to_rounded_rectangle(img_pre, pre_rounded_rectangle)
    img_pre_rounded = img_pre.convert("RGBA")
    # print(mid_extra_x , back_extra_x,mid_extra_y , back_extra_y)
    # blended_image = Image.blend(cropped_image, image_white, transparency)
    left, top = mid_extra_x + back_extra_x,mid_extra_y + back_extra_y
    cropped_img = new_img.crop((left, top, left + pre_w, top + pre_h))
    transparency_pre = 0
    blended_image = Image.blend(img_pre_rounded, cropped_img, transparency_pre)

    new_img.paste(blended_image,(left, top),blended_image)
    new_img.save('./new/' + f'{base_name}.png')

if __name__ == "__main__":
    # list_pic = ['2.png','3.png','4.png','1.png']
    path_new = './new/'
    for f in os.listdir(path_new):
        os.remove(path_new+f)
    path_1 = './old/'
    list_pic = os.listdir(path_1)
    for pic in list_pic:
        pic_paht = path_1 + pic
        main(pic_paht,2)


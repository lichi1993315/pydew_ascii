from os import walk
import pygame
import os
import sys
import tempfile
import shutil

def safe_print(text, **kwargs):
    """安全打印函数，避免emoji字符编码错误"""
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        # 如果出现编码错误，尝试替换emoji字符
        try:
            # 替换常见的emoji字符
            safe_text = text.replace('⚠️', '[WARNING]').replace('❌', '[ERROR]').replace('✅', '[OK]')
            print(safe_text, **kwargs)
        except Exception:
            # 如果还是失败，使用ASCII编码
            try:
                ascii_text = text.encode('ascii', errors='ignore').decode('ascii')
                print(ascii_text, **kwargs)
            except Exception:
                # 最后的备选方案
                print("[ENCODING ERROR] Cannot display message", **kwargs)

def import_folder(path):
	surface_list = []

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def import_folder_dict(path):
	surface_dict = {}

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[image.split('.')[0]] = image_surf

	return surface_dict


def get_resource_path(relative_path):
	"""
	获取资源文件的绝对路径
	支持开发环境和PyInstaller打包后的环境
	"""
	try:
		# PyInstaller打包后的临时目录
		base_path = sys._MEIPASS
	except AttributeError:
		# 开发环境
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, relative_path)
# def get_resource_path(relative_path):
# 	"""
# 	获取资源文件的正确路径，兼容开发环境和打包后的exe环境
# 	对于PyInstaller环境，如果遇到权限问题，返回None让调用方使用备选方案
# 	"""
# 	if hasattr(sys, '_MEIPASS'):
# 		# PyInstaller打包后的环境
# 		base_path = sys._MEIPASS
# 		full_path = os.path.join(base_path, relative_path)
# 		# 将路径分隔符标准化为系统格式
# 		full_path = os.path.normpath(full_path)
		
# 		# 检查文件是否存在并可读
# 		if os.path.exists(full_path):
# 			try:
# 				# 尝试打开文件检查权限
# 				with open(full_path, 'rb') as f:
# 					f.read(1)
# 				return full_path
# 			except PermissionError:
# 				# 权限被拒绝时，对于字体文件返回None，让字体管理器使用系统字体
# 				if 'fonts' in relative_path:
# 					return None
# 				return full_path
		
# 		return full_path
# 	else:
# 		# 开发环境
# 		# 获取项目根目录（从src/core向上两级）
# 		base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 		full_path = os.path.join(base_path, relative_path)
# 		full_path = os.path.normpath(full_path)
# 		return full_path
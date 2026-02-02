#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blender 超高端太空移民渲染 - Cycles 最高规格

场景：未来空间站围绕行星旋转，人类移民到新的家园
渲染规格：超高质量，电影级效果
"""

import bpy
import math
import random
from mathutils import Color

# 清理场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置渲染引擎为 Cycles（最高规格）
bpy.context.scene.render.engine = 'CYCLES'

# GPU 加速
bpy.context.scene.cycles.device = 'GPU'

# 超高质量渲染设置
bpy.context.scene.cycles.samples = 3000  # 超高采样数
bpy.context.scene.cycles.max_bounces = 20  # 光线反弹次数
bpy.context.scene.cycles.transparent_max_bounces = 20
bpy.context.scene.cycles.transmission_bounces = 20
bpy.context.scene.cycles.volume_bounces = 8
bpy.context.scene.cycles.diffuse_bounces = 6
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.ao_bounces = 3
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

# 噪点阈值设置（更精细的控制）
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPTIX'  # 使用NVIDIA AI降噪
bpy.context.scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'

# 高级采样设置
bpy.context.scene.cycles.progressive = 'PATH'
bpy.context.scene.cycles.use_adaptive_sampling = True
bpy.context.scene.cycles.adaptive_threshold = 0.01

# 设置渲染分辨率
bpy.context.scene.render.resolution_x = 7680  # 8K 超高清
bpy.context.scene.render.resolution_y = 4320
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.pixel_aspect_x = 1.0
bpy.context.scene.render.pixel_aspect_y = 1.0

# 输出设置
bpy.context.scene.render.filepath = '/home/lejurobot/clawd/space_colonization_8k.png'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'
bpy.context.scene.render.image_settings.color_depth = '16'

# 创建摄像机（高端设置）
camera = bpy.data.cameras.new(name="Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
bpy.context.collection.objects.link(camera_obj)
bpy.context.scene.camera = camera_obj
camera_obj.location = (0, -30, 10)
camera_obj.rotation_euler = (math.radians(22), 0, 0)

# 摄像机高级设置
camera.dof.focus_distance = 30.0
camera.dof.aperture_fstop = 2.8  # 景深效果
camera.sensor_fit = 'HORIZONTAL'
camera.sensor_width = 36.0

def create_planet_material():
    """创建超高质量行星材质（程序化纹理）"""
    material = bpy.data.materials.new(name="PlanetMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (800, 0)

    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (200, 0)
    bsdf_node.inputs['Base Color'].default_value = (0.12, 0.35, 0.85, 1.0)
    bsdf_node.inputs['Metallic'].default_value = 0.15
    bsdf_node.inputs['Roughness'].default_value = 0.55
    bsdf_node.inputs['Subsurface'].default_value = 0.3
    bsdf_node.inputs['Sheen'].default_value = 0.1

    # 添加噪点纹理
    noise_node = nodes.new(type='ShaderNodeTexNoise')
    noise_node.location = (-200, 0)
    noise_node.inputs['Scale'].default_value = 2.0
    noise_node.inputs['Detail'].default_value = 8.0

    # 添加颜色混合
    mix_node = nodes.new(type='ShaderNodeMixRGB')
    mix_node.location = (0, 0)
    mix_node.blend_type = 'MULTIPLY'
    mix_node.inputs['Color A'].default_value = (0.1, 0.3, 0.8, 1.0)
    mix_node.inputs['Color B'].default_value = (0.15, 0.4, 0.9, 1.0)
    mix_node.inputs['Fac'].default_value = 0.3

    links.new(noise_node.outputs['Color'], mix_node.inputs['Color B'])
    links.new(mix_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    return material

def create_atmosphere_material():
    """创建超高质量大气层材质"""
    material = bpy.data.materials.new(name="AtmosphereMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (600, 0)

    # 体积着色器（大气层效果）
    volume_node = nodes.new(type='ShaderNodeVolumePrincipled')
    volume_node.location = (0, -100)
    volume_node.inputs['Density'].default_value = 0.15
    volume_node.inputs['Anisotropy'].default_value = 0.5
    volume_node.inputs['Color'].default_value = (0.6, 0.8, 1.0, 1.0)
    volume_node.inputs['Scattering'].default_value = 0.8

    links.new(volume_node.outputs['Volume'], output_node.inputs['Volume'])

    return material

def create_station_material():
    """创建超高质量空间站材质"""
    material = bpy.data.materials.new(name="StationMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (800, 0)

    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (200, 0)
    bsdf_node.inputs['Base Color'].default_value = (0.85, 0.85, 0.85, 1.0)
    bsdf_node.inputs['Metallic'].default_value = 0.95
    bsdf_node.inputs['Roughness'].default_value = 0.12
    bsdf_node.inputs['IOR'].default_value = 2.8
    bsdf_node.inputs['Coat Roughness'].default_value = 0.05

    # 添加噪点纹理增加细节
    noise_node = nodes.new(type='ShaderNodeTexNoise')
    noise_node.location = (-200, 0)
    noise_node.inputs['Scale'].default_value = 10.0
    noise_node.inputs['Detail'].default_value = 2.0

    links.new(noise_node.outputs['Fac'], bsdf_node.inputs['Roughness'])
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    return material

def create_solar_material():
    """创建超高质量太阳能板材质"""
    material = bpy.data.materials.new(name="SolarMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (800, 0)

    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (200, 0)
    bsdf_node.inputs['Base Color'].default_value = (0.08, 0.18, 0.65, 1.0)
    bsdf_node.inputs['Metallic'].default_value = 0.6
    bsdf_node.inputs['Roughness'].default_value = 0.22
    bsdf_node.inputs['IOR'].default_value = 1.8

    # 添加网格纹理
    voronoi_node = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi_node.location = (-200, 0)
    voronoi_node.inputs['Scale'].default_value = 5.0

    links.new(voronoi_node.outputs['Fac'], bsdf_node.inputs['Roughness'])
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    return material

def create_star_material(brightness, size_variation):
    """创建超高质量星星材质"""
    material = bpy.data.materials.new(name=f"StarMaterial_{random.randint(0, 100000)}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (600, 0)

    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (0, 0)
    emission_node.inputs['Strength'].default_value = brightness

    # 添加颜色变化
    mix_node = nodes.new(type='ShaderNodeMixRGB')
    mix_node.location = (-200, 0)
    mix_node.blend_type = 'MIX'

    # 随机颜色（白色、淡蓝色、淡黄色）
    color_options = [
        (1.0, 1.0, 1.0, 1.0),  # 白色
        (0.9, 0.95, 1.0, 1.0),  # 淡蓝
        (1.0, 0.98, 0.9, 1.0),  # 淡黄
        (0.95, 0.95, 1.0, 1.0),  # 淡蓝白
    ]
    selected_color = color_options[random.randint(0, len(color_options)-1)]
    mix_node.inputs['Color A'].default_value = selected_color
    mix_node.inputs['Color B'].default_value = (1.0, 1.0, 1.0, 1.0)
    mix_node.inputs['Fac'].default_value = size_variation

    links.new(mix_node.outputs['Color'], emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

    return material

# 创建超高质量行星
planet_material = create_planet_material()
bpy.ops.mesh.primitive_uv_sphere_add(radius=8, segments=128, ring_count=64, location=(0, 10, 0))
planet = bpy.context.object
planet.name = "Planet"
planet.data.materials.append(planet_material)

# 创建大气层（体积材质）
atmosphere_material = create_atmosphere_material()
bpy.ops.mesh.primitive_uv_sphere_add(radius=10, segments=64, ring_count=32, location=(0, 10, 0))
atmosphere = bpy.context.object
atmosphere.name = "Atmosphere"
atmosphere.data.materials.append(atmosphere_material)

# 创建环形空间站
station_material = create_station_material()
bpy.ops.mesh.primitive_torus_add(major_radius=12, minor_radius=0.35, major_segments=256, minor_segments=64, location=(0, 0, 0))
ring = bpy.context.object
ring.name = "SpaceStationRing"
ring.rotation_euler = (math.radians(0), 0, math.radians(15))
ring.data.materials.append(station_material)

# 创建空间站核心
bpy.ops.mesh.primitive_ico_sphere_add(radius=1.5, subdivisions=4, location=(0, 0, 0))
core = bpy.context.object
core.name = "SpaceStationCore"
core.scale = (1, 0.5, 1)
core.data.materials.append(station_material)

# 添加太阳能板（4个）
solar_material = create_solar_material()
solar_positions = [(15, 0, 0), (-15, 0, 0), (0, 15, 0), (0, -15, 0)]
for i, pos in enumerate(solar_positions):
    bpy.ops.mesh.primitive_cube_add(size=4, location=pos)
    solar = bpy.context.object
    solar.name = f"SolarPanel_{i+1}"
    solar.scale = (1, 1, 0.08)
    # 增加分段数以获得更好的阴影
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    solar.data.materials.append(solar_material)

# 创建星空背景（1000颗星星）
for i in range(1000):
    star_x = random.uniform(-150, 150)
    star_y = random.uniform(-150, 150)
    star_z = random.uniform(-150, 150)

    # 创建星星
    brightness = random.uniform(0.8, 5.0)
    size_variation = random.uniform(0.1, 0.5)
    star_material = create_star_material(brightness, size_variation)

    radius = random.uniform(0.05, 0.5)
    segments = 16 if radius > 0.2 else 8
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments, ring_count=segments//2, location=(star_x, star_y, star_z))
    star = bpy.context.object
    star.name = f"Star_{i}"
    star.data.materials.append(star_material)

# 创建超高质量灯光系统
# 主太阳光
sun_light = bpy.data.lights.new(name="SunLight", type='SUN')
sun_light.energy = 8.0
sun_light.angle = 0.5  # 太阳直径
sun_light.shadow_soft_size = 2.0  # 软阴影
sun_light_obj = bpy.data.objects.new("SunLight", sun_light)
bpy.context.collection.objects.link(sun_light_obj)
sun_light_obj.location = (50, -50, 30)
sun_light_obj.rotation_euler = (math.radians(30), 0, math.radians(-45))

# 边缘光（rim light）
rim_light = bpy.data.lights.new(name="RimLight", type='SPOT')
rim_light.energy = 3.0
rim_light.spot_size = math.radians(45)
rim_light.spot_blend = 0.5
rim_light.shadow_soft_size = 1.0
rim_light_obj = bpy.data.objects.new("RimLight", rim_light)
bpy.context.collection.objects.link(rim_light_obj)
rim_light_obj.location = (-30, 30, 15)
rim_light_obj.rotation_euler = (math.radians(45), 0, math.radians(135))

# 填充光
fill_light = bpy.data.lights.new(name="FillLight", type='AREA')
fill_light.energy = 1.5
fill_light.size = 10.0
fill_light.color = (0.7, 0.8, 0.9, 1.0)
fill_light_obj = bpy.data.objects.new("FillLight", fill_light)
bpy.context.collection.objects.link(fill_light_obj)
fill_light_obj.location = (-20, -20, 10)
fill_light_obj.rotation_euler = (math.radians(30), 0, math.radians(225))

# 反射光
reflection_light = bpy.data.lights.new(name="ReflectionLight", type='POINT')
reflection_light.energy = 2.5
reflection_light.color = (0.6, 0.8, 1.0, 1.0)
reflection_light.shadow_soft_size = 0.5
reflection_light_obj = bpy.data.objects.new("ReflectionLight", reflection_light)
bpy.context.collection.objects.link(reflection_light_obj)
reflection_light_obj.location = (-25, 25, 12)

# 设置超高质量环境
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Strength'].default_value = 0.08

# 添加后期处理（Filmic 色调映射）
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Very High Contrast'
bpy.context.scene.view_settings.exposure = 1.0
bpy.context.scene.view_settings.gamma = 1.0

# 保存文件
bpy.ops.wm.save_as_mainfile(filepath='/home/lejurobot/clawd/space_colonization_8k.blend')
print("超高端场景已保存为 /home/lejurobot/clawd/space_colonization_8k.blend")

# 开始渲染
print("开始8K超高端渲染...")
print("预计时间：30-60分钟（取决于硬件性能）")
bpy.ops.render.render(write_still=True)
print(f"8K超高端渲染完成！文件保存为：{bpy.context.scene.render.filepath}")

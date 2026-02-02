#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blender 高端太空移民渲染 - 使用 Cycles 渲染器

场景：未来空间站围绕行星旋转，人类移民到新的家园
"""

import bpy
import math
import random

# 清理场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置渲染引擎为 Cycles（高端渲染）
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'  # 使用 GPU 加速
bpy.context.scene.cycles.samples = 500  # 高采样数，更高质量
bpy.context.scene.cycles.max_bounces = 8  # 光线反弹次数
bpy.context.scene.cycles.transparent_max_bounces = 8
bpy.context.scene.cycles.transmission_bounces = 8
bpy.context.scene.cycles.volume_bounces = 4

# 设置渲染分辨率
bpy.context.scene.render.resolution_x = 3840
bpy.context.scene.render.resolution_y = 2160
bpy.context.scene.render.resolution_percentage = 100

# 创建摄像机
camera = bpy.data.cameras.new(name="Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
bpy.context.collection.objects.link(camera_obj)
bpy.context.scene.camera = camera_obj
camera_obj.location = (0, -25, 8)
camera_obj.rotation_euler = (math.radians(20), 0, 0)

# 创建行星
planet_material = bpy.data.materials.new(name="PlanetMaterial")
planet_material.use_nodes = True
nodes = planet_material.node_tree.nodes
links = planet_material.node_tree.links

# 清理默认节点
for node in nodes:
    nodes.remove(node)

# 创建节点布局
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf_node.location = (0, 0)
bsdf_node.inputs['Base Color'].default_value = (0.1, 0.3, 0.8, 1.0)  # 蓝色行星
bsdf_node.inputs['Metallic'].default_value = 0.2
bsdf_node.inputs['Roughness'].default_value = 0.7

links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

# 创建行星球体
bpy.ops.mesh.primitive_uv_sphere_add(radius=8, location=(0, 10, 0))
planet = bpy.context.object
planet.name = "Planet"
planet.material_slots.create()
planet.material_slots[0].material = planet_material

# 创建大气层
atmosphere_material = bpy.data.materials.new(name="AtmosphereMaterial")
atmosphere_material.use_nodes = True
nodes = atmosphere_material.node_tree.nodes
links = atmosphere_material.node_tree.links

for node in nodes:
    nodes.remove(node)

output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (500, 0)

bsdf_node = nodes.new(type='ShaderNodeBsdfTransparent')
bsdf_node.location = (0, 100)
links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

glass_node = nodes.new(type='ShaderNodeBsdfGlass')
glass_node.location = (0, 0)
glass_node.inputs['Roughness'].default_value = 0.0
glass_node.inputs['IOR'].default_value = 1.0
links.new(glass_node.outputs['BSDF'], output_node.inputs['Surface'])

mix_node = nodes.new(type='ShaderNodeMixShader')
mix_node.location = (200, 50)
mix_node.inputs['Fac'].default_value = 0.3
links.new(bsdf_node.outputs['BSDF'], mix_node.inputs[1])
links.new(glass_node.outputs['BSDF'], mix_node.inputs[2])
links.new(mix_node.outputs['Shader'], output_node.inputs['Surface'])

# 创建大气层球体
bpy.ops.mesh.primitive_uv_sphere_add(radius=8.5, location=(0, 10, 0))
atmosphere = bpy.context.object
atmosphere.name = "Atmosphere"
atmosphere.scale = (1.02, 1.02, 1.02)
atmosphere.material_slots.create()
atmosphere.material_slots[0].material = atmosphere_material

# 创建空间站（环形结构）
station_material = bpy.data.materials.new(name="StationMaterial")
station_material.use_nodes = True
nodes = station_material.node_tree.nodes
links = station_material.node_tree.links

for node in nodes:
    nodes.remove(node)

output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf_node.location = (0, 0)
bsdf_node.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)  # 白色金属
bsdf_node.inputs['Metallic'].default_value = 0.9
bsdf_node.inputs['Roughness'].default_value = 0.2
bsdf_node.inputs['IOR'].default_value = 2.5

links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

# 创建环形空间站
bpy.ops.mesh.primitive_torus_add(major_radius=12, minor_radius=0.3, location=(0, 0, 0))
ring = bpy.context.object
ring.name = "SpaceStationRing"
ring.rotation_euler = (math.radians(0), 0, math.radians(15))
ring.material_slots.create()
ring.material_slots[0].material = station_material

# 创建空间站核心
bpy.ops.mesh.primitive_ico_sphere_add(radius=1.5, location=(0, 0, 0))
core = bpy.context.object
core.name = "SpaceStationCore"
core.scale = (1, 0.5, 1)
core.material_slots.create()
core.material_slots[0].material = station_material

# 添加太阳能板（4个）
solar_material = bpy.data.materials.new(name="SolarMaterial")
solar_material.use_nodes = True
nodes = solar_material.node_tree.nodes
links = solar_material.node_tree.links

for node in nodes:
    nodes.remove(node)

output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf_node.location = (0, 0)
bsdf_node.inputs['Base Color'].default_value = (0.1, 0.2, 0.6, 1.0)  # 深蓝色太阳能板
bsdf_node.inputs['Metallic'].default_value = 0.5
bsdf_node.inputs['Roughness'].default_value = 0.3

links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

# 创建4个太阳能板
solar_positions = [(15, 0, 0), (-15, 0, 0), (0, 15, 0), (0, -15, 0)]
for i, pos in enumerate(solar_positions):
    bpy.ops.mesh.primitive_cube_add(size=4, location=pos)
    solar = bpy.context.object
    solar.name = f"SolarPanel_{i+1}"
    solar.scale = (1, 1, 0.1)
    solar.material_slots.create()
    solar.material_slots[0].material = solar_material

# 创建星空背景
for i in range(500):
    star_x = random.uniform(-100, 100)
    star_y = random.uniform(-100, 100)
    star_z = random.uniform(-100, 100)

    # 创建星星点
    star_material = bpy.data.materials.new(name=f"StarMaterial_{i}")
    star_material.use_nodes = True
    nodes = star_material.node_tree.nodes
    links = star_material.node_tree.links

    for node in nodes:
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)

    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (0, 0)
    brightness = random.uniform(0.5, 2.0)
    emission_node.inputs['Strength'].default_value = brightness

    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.1, 0.3), location=(star_x, star_y, star_z))
    star = bpy.context.object
    star.name = f"Star_{i}"
    star.material_slots.create()
    star.material_slots[0].material = star_material

# 创建灯光
# 太阳光（平行光）
sun_light = bpy.data.lights.new(name="SunLight", type='SUN')
sun_light.energy = 5.0
sun_light_obj = bpy.data.objects.new("SunLight", sun_light)
bpy.context.collection.objects.link(sun_light_obj)
sun_light_obj.location = (50, -50, 30)
sun_light_obj.rotation_euler = (math.radians(30), 0, math.radians(-45))

# 环境光
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Strength'].default_value = 0.1  # 暗色背景

# 添加一些反射光
light_data = bpy.data.lights.new(name="ReflectionLight", type='POINT')
light_data.energy = 2.0
light_data.color = (0.8, 0.9, 1.0)
light_obj = bpy.data.objects.new("ReflectionLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-20, 20, 10)

# 保存文件
bpy.ops.wm.save_as_mainfile(filepath='/home/lejurobot/clawd/space_colonization.blend')
print("场景已保存为 /home/lejurobot/clawd/space_colonization.blend")

# 开始渲染
print("开始渲染...")
bpy.ops.render.render(write_still=True)
print(f"渲染完成！文件保存为：{bpy.context.scene.render.filepath}")

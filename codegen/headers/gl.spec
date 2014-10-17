# gl.spec file
# DON'T REMOVE PREVIOUS LINE!!! libspec depends on it!
#
# THIS FILE IS OBSOLETE. Please migrate away from using the
# ".spec" files to the XML Registry. See
#   http://www.opengl.org/registry/api/README.txt
# for more information.
#
# Copyright (c) 1991-2005 Silicon Graphics, Inc. All Rights Reserved.
# Copyright (c) 2006-2013 The Khronos Group Inc.
#
# This document is licensed under the SGI Free Software B License Version
# 2.0. For details, see http://oss.sgi.com/projects/FreeB/ .
#
# $Revision: 22299 $ on $Date: 2013-07-09 02:13:54 -0700 (Tue, 09 Jul 2013) $

required-props:
# Description of a parameter
param:		retval retained
# Display list flags
dlflags:	notlistable handcode prepad
# GLX implementation flags
glxflags:	client-intercept client-handcode server-handcode EXT SGI ignore ARB
# Vector ('v') equivalent form of a command taking 1-4 explicit xyzw/rgba arguments
vectorequiv:	*
# Category a function falls in. While there are many categories for
# early GL 1.0 functions, later functions just have a core version
# (e.g. VERSION_major_minor) or extension name for the category.
category: display-list drawing drawing-control feedback framebuf misc modeling pixel-op pixel-rw state-req xform
category: VERSION_1_0 VERSION_1_1 VERSION_1_2 VERSION_1_3 VERSION_1_4 VERSION_1_5 VERSION_2_0 VERSION_2_1 VERSION_3_0 VERSION_3_1 VERSION_3_2 VERSION_3_3 VERSION_4_0 VERSION_4_1 VERSION_4_2 VERSION_4_3
category: 3DFX_tbuffer
category: AMD_conservative_depth AMD_debug_output AMD_draw_buffers_blend AMD_multi_draw_indirect AMD_name_gen_delete AMD_performance_monitor AMD_sample_positions AMD_sparse_texture AMD_stencil_operation_extended AMD_vertex_shader_tessellator
category: APPLE_aux_depth_stencil APPLE_element_array APPLE_fence APPLE_float_pixels APPLE_flush_buffer_range APPLE_object_purgeable APPLE_row_bytes APPLE_texture_range APPLE_vertex_array_object APPLE_vertex_array_range APPLE_vertex_program_evaluators
category: ARB_ES2_compatibility ARB_base_instance ARB_blend_func_extended ARB_cl_event ARB_color_buffer_float ARB_copy_buffer ARB_debug_output ARB_depth_buffer_float ARB_draw_buffers ARB_draw_buffers_blend ARB_draw_elements_base_vertex ARB_draw_indirect ARB_draw_instanced ARB_fragment_program ARB_fragment_shader ARB_framebuffer_object ARB_framebuffer_sRGB ARB_geometry_shader4 ARB_get_program_binary ARB_gpu_shader_fp64 ARB_half_float_vertex ARB_instanced_arrays ARB_internalformat_query ARB_map_buffer_range ARB_matrix_palette ARB_multisample ARB_multitexture ARB_occlusion_query ARB_point_parameters ARB_provoking_vertex ARB_robustness ARB_sample_shading ARB_sampler_objects ARB_separate_shader_objects ARB_shader_atomic_counters ARB_shader_image_load_store ARB_shader_objects ARB_shader_subroutine ARB_shading_language_include ARB_sync ARB_tessellation_shader ARB_texture_buffer_object ARB_texture_compression ARB_texture_compression_rgtc ARB_texture_multisample ARB_texture_rectangle ARB_texture_rg ARB_texture_storage ARB_timer_query ARB_transform_feedback2 ARB_transform_feedback3 ARB_transform_feedback_instanced ARB_transpose_matrix ARB_uniform_buffer_object ARB_vertex_array_object ARB_vertex_attrib_64bit ARB_vertex_blend ARB_vertex_buffer_object ARB_vertex_program ARB_vertex_shader ARB_vertex_type_2_10_10_10_rev ARB_viewport_array ARB_window_pos
category: ARB_clear_buffer_object ARB_compute_shader ARB_copy_image ARB_framebuffer_no_attachments ARB_internalformat_query2 ARB_invalidate_subdata ARB_multi_draw_indirect ARB_program_interface_query ARB_shader_storage_buffer_object ARB_texture_buffer_range ARB_texture_storage_multisample ARB_texture_view ARB_vertex_attrib_binding
category: ATI_draw_buffers ATI_draw_buffers ATI_element_array ATI_envmap_bumpmap ATI_fragment_shader ATI_map_object_buffer ATI_meminfo ATI_pn_triangles ATI_separate_stencil ATI_texture_env_combine3 ATI_texture_float ATI_vertex_array_object ATI_vertex_attrib_array_object ATI_vertex_streams
category: EXT_bindable_uniform EXT_blend_color EXT_blend_equation_separate EXT_blend_func_separate EXT_blend_minmax EXT_color_subtable EXT_compiled_vertex_array EXT_convolution EXT_coordinate_frame EXT_copy_texture EXT_cull_vertex EXT_depth_bounds_test EXT_direct_state_access EXT_draw_buffers2 EXT_draw_instanced EXT_draw_range_elements EXT_fog_coord EXT_framebuffer_blit EXT_framebuffer_multisample EXT_framebuffer_object EXT_geometry_shader4 EXT_gpu_program_parameters EXT_gpu_shader4 EXT_histogram EXT_index_func EXT_index_material EXT_light_texture EXT_multi_draw_arrays EXT_multisample EXT_paletted_texture EXT_pixel_transform EXT_point_parameters EXT_polygon_offset EXT_provoking_vertex EXT_secondary_color EXT_separate_shader_objects EXT_shader_image_load_store EXT_stencil_clear_tag EXT_stencil_two_side EXT_subtexture EXT_texture3D EXT_texture_buffer_object EXT_texture_integer EXT_texture_object EXT_texture_perturb_normal EXT_texture_snorm EXT_texture_swizzle EXT_timer_query EXT_transform_feedback EXT_vertex_array EXT_vertex_array_bgra EXT_vertex_attrib_64bit EXT_vertex_shader EXT_vertex_weighting EXT_x11_sync_object
category: GREMEDY_frame_terminator GREMEDY_string_marker
category: HP_image_transform
category: IBM_multimode_draw_arrays IBM_static_data IBM_vertex_array_lists
category: INGR_blend_func_separate
category: INTEL_parallel_arrays INTEL_map_texture
category: KHR_debug
category: MESAX_texture_stack MESA_resize_buffers MESA_window_pos
category: NV_bindless_texture NV_conditional_render NV_copy_image NV_depth_buffer_float NV_evaluators NV_explicit_multisample NV_fence NV_float_buffer NV_fragment_program NV_fragment_program NV_framebuffer_multisample_coverage NV_geometry_program4 NV_gpu_program4 NV_gpu_program5 NV_gpu_shader5 NV_half_float NV_half_float NV_occlusion_query NV_parameter_buffer_object NV_parameter_buffer_object2 NV_path_rendering NV_pixel_data_range NV_pixel_data_range NV_point_sprite NV_present_video NV_primitive_restart NV_primitive_restart NV_register_combiners NV_register_combiners2 NV_shader_buffer_load NV_texture_barrier NV_texture_expand_normal NV_texture_expand_normal NV_texture_multisample NV_transform_feedback NV_transform_feedback2 NV_vdpau_interop NV_vdpau_interop NV_vertex_array_range NV_vertex_attrib_integer_64bit NV_vertex_buffer_unified_memory NV_vertex_program NV_vertex_program1_1_dcc NV_vertex_program2 NV_vertex_program4 NV_video_capture NV_draw_texture
category: NVX_conditional_render
category: OES_byte_coordinates OES_fixed_point OES_single_precision OES_query_matrix
category: PGI_misc_hints
category: S3_s3tc
category: SGIS_detail_texture SGIS_fog_function SGIS_multisample SGIS_pixel_texture SGIS_point_parameters SGIS_sharpen_texture SGIS_texture4D SGIS_texture_color_mask SGIS_texture_filter4 SGIX_async SGIX_flush_raster SGIX_fragment_lighting SGIX_framezoom SGIX_igloo_interface SGIX_instruments SGIX_list_priority SGIX_pixel_texture SGIX_polynomial_ffd SGIX_reference_plane SGIX_sprite SGIX_tag_sample_buffer SGI_color_table
category: SUNX_constant_data SUN_global_alpha SUN_mesh_array SUN_triangle_list SUN_vertex

# Categories for extensions with no functions - need not be included now
#
# 3DFX_multisample 3DFX_texture_compression_FXT1
# AMD_blend_minmax_factor AMD_pinned_memory AMD_seamless_cubemap_per_texture AMD_shader_stencil_export AMD_vertex_shader_layer AMD_vertex_shader_viewport_index
# APPLE_specular_vector APPLE_transform_hint
# ARB_ES3_compatibility ARB_arrays_of_arrays ARB_compressed_texture_pixel_storage ARB_conservative_depth ARB_debug_output2 ARB_depth_clamp ARB_explicit_uniform_location ARB_fragment_coord_conventions ARB_fragment_layer_viewport ARB_half_float_pixel ARB_map_buffer_alignment ARB_pixel_buffer_object ARB_point_sprite ARB_robust_buffer_access_behavior ARB_robustness_isolation ARB_seamless_cube_map ARB_shader_image_size ARB_shading_language_100 ARB_shading_language_420pack ARB_shading_language_packing ARB_stencil_texturing ARB_texture_border_clamp ARB_texture_cube_map ARB_texture_cube_map_array ARB_texture_env_add ARB_texture_float ARB_texture_gather ARB_texture_non_power_of_two ARB_texture_query_levels ARB_texture_query_lod ARB_vertex_array_bgra
# EXT_422_pixels EXT_abgr EXT_bgra EXT_blend_logic_op EXT_blend_subtract EXT_clip_volume_hint EXT_cmyka EXT_framebuffer_sRGB EXT_index_array_formats EXT_index_texture EXT_misc_attribute EXT_packed_float EXT_packed_pixels EXT_pixel_transform_color_table EXT_rescale_normal EXT_separate_specular_color EXT_shadow_funcs EXT_shared_texture_palette EXT_stencil_wrap EXT_texture EXT_texture_array EXT_texture_compression_latc EXT_texture_compression_rgtc EXT_texture_env EXT_texture_env_add EXT_texture_env_combine EXT_texture_filter_anisotropic EXT_texture_lod_bias EXT_texture_shared_exponent EXT_vertex_array_bgra
# HP_convolution_border_modes HP_occlusion_test HP_texture_lighting
# IBM_cull_vertex IBM_rasterpos_clip
# INGR_color_clamp INGR_interlace_read
# KHR_texture_compression_astc_ldr
# MESA_pack_invert MESA_ycbcr_texture
# NV_blend_square NV_fog_distance NV_fragment_program4 NV_geometry_shader4 NV_light_max_exponent NV_packed_depth_stencil NV_shader_atomic_float NV_texgen_emboss NV_texgen_reflection NV_texture_compression_vtc NV_texture_env_combine4 NV_texture_rectangle NV_texture_shader NV_texture_shader2 NV_vertex_array_range2
# PGI_vertex_hints
# REND_screen_coordinates
# SGIS_generate_mipmap SGIS_texture_border_clamp SGIS_texture_edge_clamp SGIS_texture_lod SGIX_async_histogram SGIX_async_pixel SGIX_blend_alpha_minmax SGIX_calligraphic_fragment SGIX_clipmap SGIX_convolution_accuracy SGIX_depth_pass_instrument SGIX_depth_texture SGIX_fog_offset SGIX_fog_scale SGIX_interlace SGIX_ir_instrument1 SGIX_pixel_tiles SGIX_resample SGIX_scalebias_hint SGIX_shadow SGIX_shadow_ambient SGIX_subsample SGIX_texture_add_env SGIX_texture_coordinate_clamp SGIX_texture_lod_bias SGIX_texture_multi_buffer SGIX_texture_scale_bias SGIX_texture_select SGIX_vertex_preclip SGIX_ycrcb SGIX_ycrcb_subsample SGIX_ycrcba SGI_color_matrix SGI_texture_color_table
# SUN_convolution_border_modes SUN_slice_accum
# WIN_phong_shading WIN_specular_fog

# Core version in which a function was introduced, or against
# which an extension can be implemented
version:	1.0 1.1 1.2 1.3 1.4 1.5 2.0 2.1 3.0 3.1 3.2 3.3 4.0 4.1 4.2 4.3
# Core version in which a function was removed
deprecated:	3.1
# API profile - should only be compatibility since there are no core-only
# functions for now.
profile:	compatibility
# GLX Single, Rendering, or Vendor Private opcode
glxsingle:	*
glxropcode:	*
glxvendorpriv:	*
# WGL implementation flags (incomplete)
wglflags:	client-handcode server-handcode small-data batchable
# Drivers in which this is implemented (very incomplete)
extension:	future not_implemented soft WINSOFT NV10 NV20 NV50
# Function this aliases (indistinguishable to the GL)
alias:		*
# Mesa dispatch table offset (incomplete)
offset:		*
# These properties are picked up from NVIDIA .spec files, we don't use them
glfflags:	*
beginend:	*
glxvectorequiv: *
subcategory:	*
glextmask:	*

###############################################################################
#
# glxsingle, glxropcode, and other GLX allocations to vendors
# are used here, but the master registry for GLX is in
# /repos/ogl/trunk/doc/registry/extensions.reserved
#
# XFree86 dispatch offsets:	0-645
#				578-641     NV_vertex_program
# GLS opcodes:			0x0030-0x0269
#
###############################################################################

###############################################################################
#
# things to remember when adding an extension command
#
# - append new ARB and non-ARB extensions to the appropriate portion of
#   the spec file, in extension number order.
# - leading tabs are suggested. Whitespace of any sort may be used elsewhere.
# - set glxflags to "ignore" until GLX is updated to support the new command
# - add new data types to typemaps/spec2wire.map
# - add extension name in alphabetical order to category list
# - add commands within an extension in spec order
# - use existing command entries as a model (where possible)
# - when reserving new glxropcodes, update extensions.reserved (per above)
#
###############################################################################

# New type declarations

passthru: #include <stddef.h>

passthru: #ifndef GL_VERSION_2_0
passthru: /* GL type for program/shader text */
passthru: typedef char GLchar;
passthru: #endif
passthru:
passthru: #ifndef GL_VERSION_1_5
passthru: /* GL types for handling large vertex buffer objects */
passthru: typedef ptrdiff_t GLintptr;
passthru: typedef ptrdiff_t GLsizeiptr;
passthru: #endif
passthru:
passthru: #ifndef GL_ARB_vertex_buffer_object
passthru: /* GL types for handling large vertex buffer objects */
passthru: typedef ptrdiff_t GLintptrARB;
passthru: typedef ptrdiff_t GLsizeiptrARB;
passthru: #endif
passthru:
passthru: #ifndef GL_ARB_shader_objects
passthru: /* GL types for program/shader text and shader object handles */
passthru: typedef char GLcharARB;
passthru: typedef unsigned int GLhandleARB;
passthru: #endif
passthru:
passthru: /* GL type for "half" precision (s10e5) float data in host memory */
passthru: #ifndef GL_ARB_half_float_pixel
passthru: typedef unsigned short GLhalfARB;
passthru: #endif
passthru:
passthru: #ifndef GL_NV_half_float
passthru: typedef unsigned short GLhalfNV;
passthru: #endif
passthru:
passthru: #ifndef GLEXT_64_TYPES_DEFINED
passthru: /* This code block is duplicated in glxext.h, so must be protected */
passthru: #define GLEXT_64_TYPES_DEFINED
passthru: /* Define int32_t, int64_t, and uint64_t types for UST/MSC */
passthru: /* (as used in the GL_EXT_timer_query extension). */
passthru: #if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
passthru: #include <inttypes.h>
passthru: #elif defined(__sun__) || defined(__digital__)
passthru: #include <inttypes.h>
passthru: #if defined(__STDC__)
passthru: #if defined(__arch64__) || defined(_LP64)
passthru: typedef long int int64_t;
passthru: typedef unsigned long int uint64_t;
passthru: #else
passthru: typedef long long int int64_t;
passthru: typedef unsigned long long int uint64_t;
passthru: #endif /* __arch64__ */
passthru: #endif /* __STDC__ */
passthru: #elif defined( __VMS ) || defined(__sgi)
passthru: #include <inttypes.h>
passthru: #elif defined(__SCO__) || defined(__USLC__)
passthru: #include <stdint.h>
passthru: #elif defined(__UNIXOS2__) || defined(__SOL64__)
passthru: typedef long int int32_t;
passthru: typedef long long int int64_t;
passthru: typedef unsigned long long int uint64_t;
passthru: #elif defined(_WIN32) && defined(__GNUC__)
passthru: #include <stdint.h>
passthru: #elif defined(_WIN32)
passthru: typedef __int32 int32_t;
passthru: typedef __int64 int64_t;
passthru: typedef unsigned __int64 uint64_t;
passthru: #else
passthru: /* Fallback if nothing above works */
passthru: #include <inttypes.h>
passthru: #endif
passthru: #endif
passthru:
passthru: #ifndef GL_EXT_timer_query
passthru: typedef int64_t GLint64EXT;
passthru: typedef uint64_t GLuint64EXT;
passthru: #endif
passthru:
passthru: #ifndef GL_ARB_sync
passthru: typedef int64_t GLint64;
passthru: typedef uint64_t GLuint64;
passthru: typedef struct __GLsync *GLsync;
passthru: #endif
passthru:
passthru: #ifndef GL_ARB_cl_event
passthru: /* These incomplete types let us declare types compatible with OpenCL's cl_context and cl_event */
passthru: struct _cl_context;
passthru: struct _cl_event;
passthru: #endif
passthru:
passthru: #ifndef GL_ARB_debug_output
passthru: typedef void (APIENTRY *GLDEBUGPROCARB)(GLenum source,GLenum type,GLuint id,GLenum severity,GLsizei length,const GLchar *message,GLvoid *userParam);
passthru: #endif
passthru:
passthru: #ifndef GL_AMD_debug_output
passthru: typedef void (APIENTRY *GLDEBUGPROCAMD)(GLuint id,GLenum category,GLenum severity,GLsizei length,const GLchar *message,GLvoid *userParam);
passthru: #endif
passthru:
passthru: #ifndef GL_KHR_debug
passthru: typedef void (APIENTRY *GLDEBUGPROC)(GLenum source,GLenum type,GLuint id,GLenum severity,GLsizei length,const GLchar *message,GLvoid *userParam);
passthru: #endif
passthru:
passthru: #ifndef GL_NV_vdpau_interop
passthru: typedef GLintptr GLvdpauSurfaceNV;
passthru: #endif
passthru:
passthru: #ifndef GL_OES_fixed_point
passthru: /* GLint must be 32 bits, a relatively safe assumption on modern CPUs */
passthru: typedef GLint GLfixed;
passthru: #endif
passthru:

###############################################################################
###############################################################################
#
# OpenGL 1.0 commands
#
###############################################################################
###############################################################################

###############################################################################
#
# drawing-control commands
#
###############################################################################

CullFace(mode)
	return		void
	param		mode		CullFaceMode in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	79
	offset		152

FrontFace(mode)
	return		void
	param		mode		FrontFaceDirection in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	84
	offset		157

Hint(target, mode)
	return		void
	param		target		HintTarget in value
	param		mode		HintMode in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	85
	offset		158

LineWidth(width)
	return		void
	param		width		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	95
	offset		168

PointSize(size)
	return		void
	param		size		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	100
	offset		173

PolygonMode(face, mode)
	return		void
	param		face		MaterialFace in value
	param		mode		PolygonMode in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	101
	offset		174

Scissor(x, y, width, height)
	return		void
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	103
	offset		176

TexParameterf(target, pname, param)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	105
	wglflags	small-data
	offset		178

TexParameterfv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	106
	wglflags	small-data
	offset		179

TexParameteri(target, pname, param)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	107
	wglflags	small-data
	offset		180

TexParameteriv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	version		1.0
	glxropcode	108
	wglflags	small-data
	offset		181

TexImage1D(target, level, internalformat, width, border, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureComponentCount in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	VERSION_1_0		   # old: drawing-control
	dlflags		handcode
	glxflags	client-handcode server-handcode
	version		1.0
	glxropcode	109
	wglflags	client-handcode server-handcode
	offset		182

TexImage2D(target, level, internalformat, width, height, border, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureComponentCount in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	VERSION_1_0		   # old: drawing-control
	dlflags		handcode
	glxflags	client-handcode server-handcode
	version		1.0
	glxropcode	110
	wglflags	client-handcode server-handcode
	offset		183

###############################################################################
#
# framebuf commands
#
###############################################################################

DrawBuffer(mode)
	return		void
	param		mode		DrawBufferMode in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	126
	offset		202

Clear(mask)
	return		void
	param		mask		ClearBufferMask in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	127
	offset		203

ClearColor(red, green, blue, alpha)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	param		alpha		ColorF in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	130
	offset		206

ClearStencil(s)
	return		void
	param		s		StencilValue in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	131
	offset		207

ClearDepth(depth)
	return		void
	param		depth		Float64 in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	132
	offset		208

StencilMask(mask)
	return		void
	param		mask		MaskedStencilValue in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	133
	offset		209

ColorMask(red, green, blue, alpha)
	return		void
	param		red		Boolean in value
	param		green		Boolean in value
	param		blue		Boolean in value
	param		alpha		Boolean in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	134
	offset		210

DepthMask(flag)
	return		void
	param		flag		Boolean in value
	category	VERSION_1_0		   # old: framebuf
	version		1.0
	glxropcode	135
	offset		211

###############################################################################
#
# misc commands
#
###############################################################################

Disable(cap)
	return		void
	param		cap		EnableCap in value
	category	VERSION_1_0		   # old: misc
	version		1.0
	dlflags		handcode
	glxflags	client-handcode client-intercept
	glxropcode	138
	offset		214

Enable(cap)
	return		void
	param		cap		EnableCap in value
	category	VERSION_1_0		   # old: misc
	version		1.0
	dlflags		handcode
	glxflags	client-handcode client-intercept
	glxropcode	139
	offset		215

Finish()
	return		void
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	category	VERSION_1_0		   # old: misc
	version		1.0
	glxsingle	108
	offset		216

Flush()
	return		void
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	category	VERSION_1_0		   # old: misc
	version		1.0
	glxsingle	142
	offset		217

###############################################################################
#
# pixel-op commands
#
###############################################################################

BlendFunc(sfactor, dfactor)
	return		void
	param		sfactor		BlendingFactorSrc in value
	param		dfactor		BlendingFactorDest in value
	category	VERSION_1_0		   # old: pixel-op
	version		1.0
	glxropcode	160
	offset		241

LogicOp(opcode)
	return		void
	param		opcode		LogicOp in value
	category	VERSION_1_0		   # old: pixel-op
	version		1.0
	glxropcode	161
	offset		242

StencilFunc(func, ref, mask)
	return		void
	param		func		StencilFunction in value
	param		ref		StencilValue in value
	param		mask		MaskedStencilValue in value
	category	VERSION_1_0		   # old: pixel-op
	version		1.0
	glxropcode	162
	offset		243

StencilOp(fail, zfail, zpass)
	return		void
	param		fail		StencilOp in value
	param		zfail		StencilOp in value
	param		zpass		StencilOp in value
	category	VERSION_1_0		   # old: pixel-op
	version		1.0
	glxropcode	163
	offset		244

DepthFunc(func)
	return		void
	param		func		DepthFunction in value
	category	VERSION_1_0		   # old: pixel-op
	version		1.0
	glxropcode	164
	offset		245

###############################################################################
#
# pixel-rw commands
#
###############################################################################

PixelStoref(pname, param)
	return		void
	param		pname		PixelStoreParameter in value
	param		param		CheckedFloat32 in value
	dlflags		notlistable
	glxflags	client-handcode
	category	VERSION_1_0		   # old: pixel-rw
	version		1.0
	glxsingle	109
	wglflags	batchable
	offset		249

PixelStorei(pname, param)
	return		void
	param		pname		PixelStoreParameter in value
	param		param		CheckedInt32 in value
	dlflags		notlistable
	glxflags	client-handcode
	category	VERSION_1_0		   # old: pixel-rw
	version		1.0
	glxsingle	110
	wglflags	batchable
	offset		250

ReadBuffer(mode)
	return		void
	param		mode		ReadBufferMode in value
	category	VERSION_1_0		   # old: pixel-rw
	version		1.0
	glxropcode	171
	offset		254

ReadPixels(x, y, width, height, format, type, pixels)
	return		void
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void out array [COMPSIZE(format/type/width/height)]
	category	VERSION_1_0		   # old: pixel-rw
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.0
	glxsingle	111
	wglflags	client-handcode server-handcode
	offset		256

###############################################################################
#
# state-req commands
#
###############################################################################

GetBooleanv(pname, params)
	return		void
	param		pname		GetPName in value
	param		params		Boolean out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode
	version		1.0
	glxsingle	112
	wglflags	small-data
	offset		258

GetDoublev(pname, params)
	return		void
	param		pname		GetPName in value
	param		params		Float64 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode
	version		1.0
	glxsingle	114
	wglflags	small-data
	offset		260

GetError()
	return		ErrorCode
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode
	version		1.0
	glxsingle	115
	offset		261

GetFloatv(pname, params)
	return		void
	param		pname		GetPName in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode
	version		1.0
	glxsingle	116
	wglflags	small-data
	offset		262

GetIntegerv(pname, params)
	return		void
	param		pname		GetPName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode
	version		1.0
	glxsingle	117
	wglflags	small-data
	offset		263

GetString(name)
	return		String
	param		name		StringName in value
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.0
	glxsingle	129
	wglflags	client-handcode server-handcode
	offset		275

GetTexImage(target, level, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void out array [COMPSIZE(target/level/format/type)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.0
	glxsingle	135
	wglflags	client-handcode server-handcode
	offset		281

GetTexParameterfv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	version		1.0
	glxsingle	136
	wglflags	small-data
	offset		282

GetTexParameteriv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	version		1.0
	glxsingle	137
	wglflags	small-data
	offset		283

GetTexLevelParameterfv(target, level, pname, params)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		pname		GetTextureParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	version		1.0
	glxsingle	138
	wglflags	small-data
	offset		284

GetTexLevelParameteriv(target, level, pname, params)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	version		1.0
	glxsingle	139
	wglflags	small-data
	offset		285

IsEnabled(cap)
	return		Boolean
	param		cap		EnableCap in value
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	version		1.0
	glxflags	client-handcode client-intercept
	glxsingle	140
	offset		286

###############################################################################
#
# xform commands
#
###############################################################################

DepthRange(near, far)
	return		void
	param		near		Float64 in value
	param		far		Float64 in value
	category	VERSION_1_0		   # old: xform
	version		1.0
	glxropcode	174
	offset		288

Viewport(x, y, width, height)
	return		void
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	VERSION_1_0		   # old: xform
	version		1.0
	glxropcode	191
	offset		305

###############################################################################
###############################################################################
#
# OpenGL 1.0 deprecated commands
#
###############################################################################
###############################################################################

# display-list commands

NewList(list, mode)
	return		void
	param		list		List in value
	param		mode		ListMode in value
	dlflags		notlistable
	category	VERSION_1_0		   # old: display-list
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	101
	wglflags	batchable
	offset		0

EndList()
	return		void
	dlflags		notlistable
	category	VERSION_1_0		   # old: display-list
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	102
	wglflags	batchable
	offset		1

CallList(list)
	return		void
	param		list		List in value
	category	VERSION_1_0		   # old: display-list
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	1
	offset		2

CallLists(n, type, lists)
	return		void
	param		n		SizeI in value
	param		type		ListNameType in value
	param		lists		Void in array [COMPSIZE(n/type)]
	category	VERSION_1_0		   # old: display-list
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	2
	offset		3

DeleteLists(list, range)
	return		void
	param		list		List in value
	param		range		SizeI in value
	dlflags		notlistable
	category	VERSION_1_0		   # old: display-list
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	103
	wglflags	batchable
	offset		4

GenLists(range)
	return		List
	param		range		SizeI in value
	dlflags		notlistable
	category	VERSION_1_0		   # old: display-list
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	104
	offset		5

ListBase(base)
	return		void
	param		base		List in value
	category	VERSION_1_0		   # old: display-list
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	3
	offset		6

# drawing commands

Begin(mode)
	return		void
	param		mode		PrimitiveType in value
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	4
	offset		7

Bitmap(width, height, xorig, yorig, xmove, ymove, bitmap)
	return		void
	param		width		SizeI in value
	param		height		SizeI in value
	param		xorig		CoordF in value
	param		yorig		CoordF in value
	param		xmove		CoordF in value
	param		ymove		CoordF in value
	param		bitmap		UInt8 in array [COMPSIZE(width/height)]
	category	VERSION_1_0		   # old: drawing
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	5
	wglflags	client-handcode server-handcode
	offset		8

Color3b(red, green, blue)
	return		void
	param		red		ColorB in value
	param		green		ColorB in value
	param		blue		ColorB in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3bv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		9

Color3bv(v)
	return		void
	param		v		ColorB in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	6
	offset		10

Color3d(red, green, blue)
	return		void
	param		red		ColorD in value
	param		green		ColorD in value
	param		blue		ColorD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		11

Color3dv(v)
	return		void
	param		v		ColorD in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	7
	offset		12

Color3f(red, green, blue)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		13

Color3fv(v)
	return		void
	param		v		ColorF in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	8
	offset		14

Color3i(red, green, blue)
	return		void
	param		red		ColorI in value
	param		green		ColorI in value
	param		blue		ColorI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		15

Color3iv(v)
	return		void
	param		v		ColorI in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	9
	offset		16

Color3s(red, green, blue)
	return		void
	param		red		ColorS in value
	param		green		ColorS in value
	param		blue		ColorS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		17

Color3sv(v)
	return		void
	param		v		ColorS in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	10
	offset		18

Color3ub(red, green, blue)
	return		void
	param		red		ColorUB in value
	param		green		ColorUB in value
	param		blue		ColorUB in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3ubv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		19

Color3ubv(v)
	return		void
	param		v		ColorUB in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	11
	offset		20

Color3ui(red, green, blue)
	return		void
	param		red		ColorUI in value
	param		green		ColorUI in value
	param		blue		ColorUI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3uiv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		21

Color3uiv(v)
	return		void
	param		v		ColorUI in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	12
	offset		22

Color3us(red, green, blue)
	return		void
	param		red		ColorUS in value
	param		green		ColorUS in value
	param		blue		ColorUS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color3usv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		23

Color3usv(v)
	return		void
	param		v		ColorUS in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	13
	offset		24

Color4b(red, green, blue, alpha)
	return		void
	param		red		ColorB in value
	param		green		ColorB in value
	param		blue		ColorB in value
	param		alpha		ColorB in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4bv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		25

Color4bv(v)
	return		void
	param		v		ColorB in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	14
	offset		26

Color4d(red, green, blue, alpha)
	return		void
	param		red		ColorD in value
	param		green		ColorD in value
	param		blue		ColorD in value
	param		alpha		ColorD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		27

Color4dv(v)
	return		void
	param		v		ColorD in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	15
	offset		28

Color4f(red, green, blue, alpha)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	param		alpha		ColorF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		29

Color4fv(v)
	return		void
	param		v		ColorF in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	16
	offset		30

Color4i(red, green, blue, alpha)
	return		void
	param		red		ColorI in value
	param		green		ColorI in value
	param		blue		ColorI in value
	param		alpha		ColorI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		31

Color4iv(v)
	return		void
	param		v		ColorI in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	17
	offset		32

Color4s(red, green, blue, alpha)
	return		void
	param		red		ColorS in value
	param		green		ColorS in value
	param		blue		ColorS in value
	param		alpha		ColorS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		33

Color4sv(v)
	return		void
	param		v		ColorS in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	18
	offset		34

Color4ub(red, green, blue, alpha)
	return		void
	param		red		ColorUB in value
	param		green		ColorUB in value
	param		blue		ColorUB in value
	param		alpha		ColorUB in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4ubv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		35

Color4ubv(v)
	return		void
	param		v		ColorUB in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	19
	offset		36

Color4ui(red, green, blue, alpha)
	return		void
	param		red		ColorUI in value
	param		green		ColorUI in value
	param		blue		ColorUI in value
	param		alpha		ColorUI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4uiv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		37

Color4uiv(v)
	return		void
	param		v		ColorUI in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	20
	offset		38

Color4us(red, green, blue, alpha)
	return		void
	param		red		ColorUS in value
	param		green		ColorUS in value
	param		blue		ColorUS in value
	param		alpha		ColorUS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Color4usv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		39

Color4usv(v)
	return		void
	param		v		ColorUS in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	21
	offset		40

EdgeFlag(flag)
	return		void
	param		flag		Boolean in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	EdgeFlagv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		41

EdgeFlagv(flag)
	return		void
	param		flag		Boolean in reference
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	22
	offset		42

End()
	return		void
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	23
	offset		43

Indexd(c)
	return		void
	param		c		ColorIndexValueD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Indexdv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		44

Indexdv(c)
	return		void
	param		c		ColorIndexValueD in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	24
	offset		45

Indexf(c)
	return		void
	param		c		ColorIndexValueF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Indexfv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		46

Indexfv(c)
	return		void
	param		c		ColorIndexValueF in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	25
	offset		47

Indexi(c)
	return		void
	param		c		ColorIndexValueI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Indexiv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		48

Indexiv(c)
	return		void
	param		c		ColorIndexValueI in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	26
	offset		49

Indexs(c)
	return		void
	param		c		ColorIndexValueS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Indexsv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		50

Indexsv(c)
	return		void
	param		c		ColorIndexValueS in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	27
	offset		51

Normal3b(nx, ny, nz)
	return		void
	param		nx		Int8 in value
	param		ny		Int8 in value
	param		nz		Int8 in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Normal3bv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		52

Normal3bv(v)
	return		void
	param		v		Int8 in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	28
	offset		53

Normal3d(nx, ny, nz)
	return		void
	param		nx		CoordD in value
	param		ny		CoordD in value
	param		nz		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Normal3dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		54

Normal3dv(v)
	return		void
	param		v		CoordD in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	29
	offset		55

Normal3f(nx, ny, nz)
	return		void
	param		nx		CoordF in value
	param		ny		CoordF in value
	param		nz		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Normal3fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		56

Normal3fv(v)
	return		void
	param		v		CoordF in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	30
	offset		57

Normal3i(nx, ny, nz)
	return		void
	param		nx		Int32 in value
	param		ny		Int32 in value
	param		nz		Int32 in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Normal3iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		58

Normal3iv(v)
	return		void
	param		v		Int32 in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	31
	offset		59

Normal3s(nx, ny, nz)
	return		void
	param		nx		Int16 in value
	param		ny		Int16 in value
	param		nz		Int16 in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Normal3sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		60

Normal3sv(v)
	return		void
	param		v		Int16 in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	32
	offset		61

RasterPos2d(x, y)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos2dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		62

RasterPos2dv(v)
	return		void
	param		v		CoordD in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	33
	offset		63

RasterPos2f(x, y)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos2fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		64

RasterPos2fv(v)
	return		void
	param		v		CoordF in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	34
	offset		65

RasterPos2i(x, y)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos2iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		66

RasterPos2iv(v)
	return		void
	param		v		CoordI in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	35
	offset		67

RasterPos2s(x, y)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos2sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		68

RasterPos2sv(v)
	return		void
	param		v		CoordS in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	36
	offset		69

RasterPos3d(x, y, z)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	vectorequiv	RasterPos3dv
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		70

RasterPos3dv(v)
	return		void
	param		v		CoordD in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	37
	offset		71

RasterPos3f(x, y, z)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos3fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		72

RasterPos3fv(v)
	return		void
	param		v		CoordF in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	38
	offset		73

RasterPos3i(x, y, z)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos3iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		74

RasterPos3iv(v)
	return		void
	param		v		CoordI in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	39
	offset		75

RasterPos3s(x, y, z)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos3sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		76

RasterPos3sv(v)
	return		void
	param		v		CoordS in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	40
	offset		77

RasterPos4d(x, y, z, w)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	param		w		CoordD in value
	vectorequiv	RasterPos4dv
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		78

RasterPos4dv(v)
	return		void
	param		v		CoordD in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	41
	offset		79

RasterPos4f(x, y, z, w)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	param		w		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos4fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		80

RasterPos4fv(v)
	return		void
	param		v		CoordF in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	42
	offset		81

RasterPos4i(x, y, z, w)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	param		w		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos4iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		82

RasterPos4iv(v)
	return		void
	param		v		CoordI in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	43
	offset		83

RasterPos4s(x, y, z, w)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	param		w		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	RasterPos4sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		84

RasterPos4sv(v)
	return		void
	param		v		CoordS in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	44
	offset		85

Rectd(x1, y1, x2, y2)
	return		void
	param		x1		CoordD in value
	param		y1		CoordD in value
	param		x2		CoordD in value
	param		y2		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Rectdv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		86

Rectdv(v1, v2)
	return		void
	param		v1		CoordD in array [2]
	param		v2		CoordD in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	45
	offset		87

Rectf(x1, y1, x2, y2)
	return		void
	param		x1		CoordF in value
	param		y1		CoordF in value
	param		x2		CoordF in value
	param		y2		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Rectfv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		88

Rectfv(v1, v2)
	return		void
	param		v1		CoordF in array [2]
	param		v2		CoordF in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	46
	offset		89

Recti(x1, y1, x2, y2)
	return		void
	param		x1		CoordI in value
	param		y1		CoordI in value
	param		x2		CoordI in value
	param		y2		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Rectiv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		90

Rectiv(v1, v2)
	return		void
	param		v1		CoordI in array [2]
	param		v2		CoordI in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	47
	offset		91

Rects(x1, y1, x2, y2)
	return		void
	param		x1		CoordS in value
	param		y1		CoordS in value
	param		x2		CoordS in value
	param		y2		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Rectsv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		92

Rectsv(v1, v2)
	return		void
	param		v1		CoordS in array [2]
	param		v2		CoordS in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	48
	offset		93

TexCoord1d(s)
	return		void
	param		s		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord1dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		94

TexCoord1dv(v)
	return		void
	param		v		CoordD in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	49
	offset		95

TexCoord1f(s)
	return		void
	param		s		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord1fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		96

TexCoord1fv(v)
	return		void
	param		v		CoordF in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	50
	offset		97

TexCoord1i(s)
	return		void
	param		s		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord1iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		98

TexCoord1iv(v)
	return		void
	param		v		CoordI in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	51
	offset		99

TexCoord1s(s)
	return		void
	param		s		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord1sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		100

TexCoord1sv(v)
	return		void
	param		v		CoordS in array [1]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	52
	offset		101

TexCoord2d(s, t)
	return		void
	param		s		CoordD in value
	param		t		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord2dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		102

TexCoord2dv(v)
	return		void
	param		v		CoordD in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	53
	offset		103

TexCoord2f(s, t)
	return		void
	param		s		CoordF in value
	param		t		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord2fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		104

TexCoord2fv(v)
	return		void
	param		v		CoordF in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	54
	offset		105

TexCoord2i(s, t)
	return		void
	param		s		CoordI in value
	param		t		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord2iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		106

TexCoord2iv(v)
	return		void
	param		v		CoordI in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	55
	offset		107

TexCoord2s(s, t)
	return		void
	param		s		CoordS in value
	param		t		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord2sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		108

TexCoord2sv(v)
	return		void
	param		v		CoordS in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	56
	offset		109

TexCoord3d(s, t, r)
	return		void
	param		s		CoordD in value
	param		t		CoordD in value
	param		r		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord3dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		110

TexCoord3dv(v)
	return		void
	param		v		CoordD in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	57
	offset		111

TexCoord3f(s, t, r)
	return		void
	param		s		CoordF in value
	param		t		CoordF in value
	param		r		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord3fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		112

TexCoord3fv(v)
	return		void
	param		v		CoordF in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	58
	offset		113

TexCoord3i(s, t, r)
	return		void
	param		s		CoordI in value
	param		t		CoordI in value
	param		r		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord3iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		114

TexCoord3iv(v)
	return		void
	param		v		CoordI in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	59
	offset		115

TexCoord3s(s, t, r)
	return		void
	param		s		CoordS in value
	param		t		CoordS in value
	param		r		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord3sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		116

TexCoord3sv(v)
	return		void
	param		v		CoordS in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	60
	offset		117

TexCoord4d(s, t, r, q)
	return		void
	param		s		CoordD in value
	param		t		CoordD in value
	param		r		CoordD in value
	param		q		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord4dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		118

TexCoord4dv(v)
	return		void
	param		v		CoordD in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	61
	offset		119

TexCoord4f(s, t, r, q)
	return		void
	param		s		CoordF in value
	param		t		CoordF in value
	param		r		CoordF in value
	param		q		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord4fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		120

TexCoord4fv(v)
	return		void
	param		v		CoordF in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	62
	offset		121

TexCoord4i(s, t, r, q)
	return		void
	param		s		CoordI in value
	param		t		CoordI in value
	param		r		CoordI in value
	param		q		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord4iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		122

TexCoord4iv(v)
	return		void
	param		v		CoordI in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	63
	offset		123

TexCoord4s(s, t, r, q)
	return		void
	param		s		CoordS in value
	param		t		CoordS in value
	param		r		CoordS in value
	param		q		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	TexCoord4sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		124

TexCoord4sv(v)
	return		void
	param		v		CoordS in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	64
	offset		125

Vertex2d(x, y)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex2dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		126

Vertex2dv(v)
	return		void
	param		v		CoordD in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	65
	offset		127

Vertex2f(x, y)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex2fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		128

Vertex2fv(v)
	return		void
	param		v		CoordF in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	66
	offset		129

Vertex2i(x, y)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex2iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		130

Vertex2iv(v)
	return		void
	param		v		CoordI in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	67
	offset		131

Vertex2s(x, y)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex2sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		132

Vertex2sv(v)
	return		void
	param		v		CoordS in array [2]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	68
	offset		133

Vertex3d(x, y, z)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex3dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		134

Vertex3dv(v)
	return		void
	param		v		CoordD in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	69
	offset		135

Vertex3f(x, y, z)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex3fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		136

Vertex3fv(v)
	return		void
	param		v		CoordF in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	70
	offset		137

Vertex3i(x, y, z)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex3iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		138

Vertex3iv(v)
	return		void
	param		v		CoordI in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	71
	offset		139

Vertex3s(x, y, z)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex3sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		140

Vertex3sv(v)
	return		void
	param		v		CoordS in array [3]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	72
	offset		141

Vertex4d(x, y, z, w)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	param		w		CoordD in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex4dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		142

Vertex4dv(v)
	return		void
	param		v		CoordD in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	73
	offset		143

Vertex4f(x, y, z, w)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	param		w		CoordF in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex4fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		144

Vertex4fv(v)
	return		void
	param		v		CoordF in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	74
	offset		145

Vertex4i(x, y, z, w)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	param		w		CoordI in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex4iv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		146

Vertex4iv(v)
	return		void
	param		v		CoordI in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	75
	offset		147

Vertex4s(x, y, z, w)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	param		w		CoordS in value
	category	VERSION_1_0		   # old: drawing
	vectorequiv	Vertex4sv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		148

Vertex4sv(v)
	return		void
	param		v		CoordS in array [4]
	category	VERSION_1_0		   # old: drawing
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	76
	offset		149

ClipPlane(plane, equation)
	return		void
	param		plane		ClipPlaneName in value
	param		equation	Float64 in array [4]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	77
	offset		150

ColorMaterial(face, mode)
	return		void
	param		face		MaterialFace in value
	param		mode		ColorMaterialParameter in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	78
	offset		151

Fogf(pname, param)
	return		void
	param		pname		FogParameter in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	80
	wglflags	small-data
	offset		153

Fogfv(pname, params)
	return		void
	param		pname		FogParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	81
	wglflags	small-data
	offset		154

Fogi(pname, param)
	return		void
	param		pname		FogParameter in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	82
	wglflags	small-data
	offset		155

Fogiv(pname, params)
	return		void
	param		pname		FogParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	83
	wglflags	small-data
	offset		156

Lightf(light, pname, param)
	return		void
	param		light		LightName in value
	param		pname		LightParameter in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	86
	wglflags	small-data
	offset		159

Lightfv(light, pname, params)
	return		void
	param		light		LightName in value
	param		pname		LightParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	87
	wglflags	small-data
	offset		160

Lighti(light, pname, param)
	return		void
	param		light		LightName in value
	param		pname		LightParameter in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	88
	wglflags	small-data
	offset		161

Lightiv(light, pname, params)
	return		void
	param		light		LightName in value
	param		pname		LightParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	89
	wglflags	small-data
	offset		162

LightModelf(pname, param)
	return		void
	param		pname		LightModelParameter in value
	param		param		Float32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	90
	wglflags	small-data
	offset		163

LightModelfv(pname, params)
	return		void
	param		pname		LightModelParameter in value
	param		params		Float32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	91
	wglflags	small-data
	offset		164

LightModeli(pname, param)
	return		void
	param		pname		LightModelParameter in value
	param		param		Int32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	92
	wglflags	small-data
	offset		165

LightModeliv(pname, params)
	return		void
	param		pname		LightModelParameter in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	93
	wglflags	small-data
	offset		166

LineStipple(factor, pattern)
	return		void
	param		factor		CheckedInt32 in value
	param		pattern		LineStipple in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	94
	offset		167

Materialf(face, pname, param)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	96
	wglflags	small-data
	offset		169

Materialfv(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	97
	wglflags	small-data
	offset		170

Materiali(face, pname, param)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	98
	wglflags	small-data
	offset		171

Materialiv(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	99
	wglflags	small-data
	offset		172

PolygonStipple(mask)
	return		void
	param		mask		UInt8 in array [COMPSIZE()]
	category	VERSION_1_0		   # old: drawing-control
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	102
	wglflags	client-handcode server-handcode
	offset		175

ShadeModel(mode)
	return		void
	param		mode		ShadingModel in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	104
	offset		177

TexEnvf(target, pname, param)
	return		void
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	111
	wglflags	small-data
	offset		184

TexEnvfv(target, pname, params)
	return		void
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	112
	wglflags	small-data
	offset		185

TexEnvi(target, pname, param)
	return		void
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	113
	wglflags	small-data
	offset		186

TexEnviv(target, pname, params)
	return		void
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	114
	wglflags	small-data
	offset		187

TexGend(coord, pname, param)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		param		Float64 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	115
	wglflags	small-data
	offset		188

TexGendv(coord, pname, params)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Float64 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	116
	wglflags	small-data
	offset		189

TexGenf(coord, pname, param)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	117
	wglflags	small-data
	offset		190

TexGenfv(coord, pname, params)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	118
	wglflags	small-data
	offset		191

TexGeni(coord, pname, param)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	119
	wglflags	small-data
	offset		192

TexGeniv(coord, pname, params)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: drawing-control
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	120
	wglflags	small-data
	offset		193

# feedback commands

FeedbackBuffer(size, type, buffer)
	return		void
	param		size		SizeI in value
	param		type		FeedbackType in value
	param		buffer		FeedbackElement out array [size] retained
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	105
	wglflags	client-handcode server-handcode batchable
	offset		194

SelectBuffer(size, buffer)
	return		void
	param		size		SizeI in value
	param		buffer		SelectName out array [size] retained
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	106
	wglflags	client-handcode server-handcode batchable
	offset		195

RenderMode(mode)
	return		Int32
	param		mode		RenderingMode in value
	category	VERSION_1_0		   # old: feedback
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	107
	wglflags	client-handcode server-handcode
	offset		196

InitNames()
	return		void
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	121
	offset		197

LoadName(name)
	return		void
	param		name		SelectName in value
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	122
	offset		198

PassThrough(token)
	return		void
	param		token		FeedbackElement in value
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	123
	offset		199

PopName()
	return		void
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	124
	offset		200

PushName(name)
	return		void
	param		name		SelectName in value
	category	VERSION_1_0		   # old: feedback
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	125
	offset		201

ClearAccum(red, green, blue, alpha)
	return		void
	param		red		Float32 in value
	param		green		Float32 in value
	param		blue		Float32 in value
	param		alpha		Float32 in value
	category	VERSION_1_0		   # old: framebuf
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	128
	offset		204

ClearIndex(c)
	return		void
	param		c		MaskedColorIndexValueF in value
	category	VERSION_1_0		   # old: framebuf
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	129
	offset		205

IndexMask(mask)
	return		void
	param		mask		MaskedColorIndexValueI in value
	category	VERSION_1_0		   # old: framebuf
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	136
	offset		212

Accum(op, value)
	return		void
	param		op		AccumOp in value
	param		value		CoordF in value
	category	VERSION_1_0		   # old: misc
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	137
	offset		213

PopAttrib()
	return		void
	category	VERSION_1_0		   # old: misc
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	141
	offset		218

PushAttrib(mask)
	return		void
	param		mask		AttribMask in value
	category	VERSION_1_0		   # old: misc
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	142
	offset		219

# modeling commands

Map1d(target, u1, u2, stride, order, points)
	return		void
	param		target		MapTarget in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	param		stride		Int32 in value
	param		order		CheckedInt32 in value
	param		points		CoordD in array [COMPSIZE(target/stride/order)]
	category	VERSION_1_0		   # old: modeling
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	143
	wglflags	client-handcode server-handcode
	offset		220

Map1f(target, u1, u2, stride, order, points)
	return		void
	param		target		MapTarget in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	param		stride		Int32 in value
	param		order		CheckedInt32 in value
	param		points		CoordF in array [COMPSIZE(target/stride/order)]
	category	VERSION_1_0		   # old: modeling
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	144
	wglflags	client-handcode server-handcode
	offset		221

Map2d(target, u1, u2, ustride, uorder, v1, v2, vstride, vorder, points)
	return		void
	param		target		MapTarget in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	param		ustride		Int32 in value
	param		uorder		CheckedInt32 in value
	param		v1		CoordD in value
	param		v2		CoordD in value
	param		vstride		Int32 in value
	param		vorder		CheckedInt32 in value
	param		points		CoordD in array [COMPSIZE(target/ustride/uorder/vstride/vorder)]
	category	VERSION_1_0		   # old: modeling
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	145
	wglflags	client-handcode server-handcode
	offset		222

Map2f(target, u1, u2, ustride, uorder, v1, v2, vstride, vorder, points)
	return		void
	param		target		MapTarget in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	param		ustride		Int32 in value
	param		uorder		CheckedInt32 in value
	param		v1		CoordF in value
	param		v2		CoordF in value
	param		vstride		Int32 in value
	param		vorder		CheckedInt32 in value
	param		points		CoordF in array [COMPSIZE(target/ustride/uorder/vstride/vorder)]
	category	VERSION_1_0		   # old: modeling
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	146
	wglflags	client-handcode server-handcode
	offset		223

MapGrid1d(un, u1, u2)
	return		void
	param		un		Int32 in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	147
	offset		224

MapGrid1f(un, u1, u2)
	return		void
	param		un		Int32 in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	148
	offset		225

MapGrid2d(un, u1, u2, vn, v1, v2)
	return		void
	param		un		Int32 in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	param		vn		Int32 in value
	param		v1		CoordD in value
	param		v2		CoordD in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	149
	offset		226

MapGrid2f(un, u1, u2, vn, v1, v2)
	return		void
	param		un		Int32 in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	param		vn		Int32 in value
	param		v1		CoordF in value
	param		v2		CoordF in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	150
	offset		227

EvalCoord1d(u)
	return		void
	param		u		CoordD in value
	category	VERSION_1_0		   # old: modeling
	vectorequiv	EvalCoord1dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		228

EvalCoord1dv(u)
	return		void
	param		u		CoordD in array [1]
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	151
	offset		229

EvalCoord1f(u)
	return		void
	param		u		CoordF in value
	category	VERSION_1_0		   # old: modeling
	vectorequiv	EvalCoord1fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		230

EvalCoord1fv(u)
	return		void
	param		u		CoordF in array [1]
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	152
	offset		231

EvalCoord2d(u, v)
	return		void
	param		u		CoordD in value
	param		v		CoordD in value
	category	VERSION_1_0		   # old: modeling
	vectorequiv	EvalCoord2dv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		232

EvalCoord2dv(u)
	return		void
	param		u		CoordD in array [2]
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	153
	offset		233

EvalCoord2f(u, v)
	return		void
	param		u		CoordF in value
	param		v		CoordF in value
	category	VERSION_1_0		   # old: modeling
	vectorequiv	EvalCoord2fv
	profile		compatibility
	version		1.0
	deprecated	3.1
	offset		234

EvalCoord2fv(u)
	return		void
	param		u		CoordF in array [2]
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	154
	offset		235

EvalMesh1(mode, i1, i2)
	return		void
	param		mode		MeshMode1 in value
	param		i1		CheckedInt32 in value
	param		i2		CheckedInt32 in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	155
	offset		236

EvalPoint1(i)
	return		void
	param		i		Int32 in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	156
	offset		237

EvalMesh2(mode, i1, i2, j1, j2)
	return		void
	param		mode		MeshMode2 in value
	param		i1		CheckedInt32 in value
	param		i2		CheckedInt32 in value
	param		j1		CheckedInt32 in value
	param		j2		CheckedInt32 in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	157
	offset		238

EvalPoint2(i, j)
	return		void
	param		i		CheckedInt32 in value
	param		j		CheckedInt32 in value
	category	VERSION_1_0		   # old: modeling
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	158
	offset		239

AlphaFunc(func, ref)
	return		void
	param		func		AlphaFunction in value
	param		ref		Float32 in value
	category	VERSION_1_0		   # old: pixel-op
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	159
	offset		240

PixelZoom(xfactor, yfactor)
	return		void
	param		xfactor		Float32 in value
	param		yfactor		Float32 in value
	category	VERSION_1_0		   # old: pixel-rw
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	165
	offset		246

PixelTransferf(pname, param)
	return		void
	param		pname		PixelTransferParameter in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_0		   # old: pixel-rw
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	166
	offset		247

PixelTransferi(pname, param)
	return		void
	param		pname		PixelTransferParameter in value
	param		param		CheckedInt32 in value
	category	VERSION_1_0		   # old: pixel-rw
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	167
	offset		248

PixelMapfv(map, mapsize, values)
	return		void
	param		map		PixelMap in value
	param		mapsize		CheckedInt32 in value
	param		values		Float32 in array [mapsize]
	category	VERSION_1_0		   # old: pixel-rw
	glxflags	client-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	168
	offset		251

PixelMapuiv(map, mapsize, values)
	return		void
	param		map		PixelMap in value
	param		mapsize		CheckedInt32 in value
	param		values		UInt32 in array [mapsize]
	category	VERSION_1_0		   # old: pixel-rw
	glxflags	client-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	169
	offset		252

PixelMapusv(map, mapsize, values)
	return		void
	param		map		PixelMap in value
	param		mapsize		CheckedInt32 in value
	param		values		UInt16 in array [mapsize]
	category	VERSION_1_0		   # old: pixel-rw
	glxflags	client-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	170
	offset		253

CopyPixels(x, y, width, height, type)
	return		void
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		type		PixelCopyType in value
	category	VERSION_1_0		   # old: pixel-rw
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	172
	offset		255

DrawPixels(width, height, format, type, pixels)
	return		void
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	VERSION_1_0		   # old: pixel-rw
	dlflags		handcode
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	173
	wglflags	client-handcode server-handcode
	offset		257

GetClipPlane(plane, equation)
	return		void
	param		plane		ClipPlaneName in value
	param		equation	Float64 out array [4]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	113
	glxflags	client-handcode server-handcode
	offset		259

GetLightfv(light, pname, params)
	return		void
	param		light		LightName in value
	param		pname		LightParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	118
	wglflags	small-data
	offset		264

GetLightiv(light, pname, params)
	return		void
	param		light		LightName in value
	param		pname		LightParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	119
	wglflags	small-data
	offset		265

GetMapdv(target, query, v)
	return		void
	param		target		MapTarget in value
	param		query		GetMapQuery in value
	param		v		Float64 out array [COMPSIZE(target/query)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	120
	offset		266

GetMapfv(target, query, v)
	return		void
	param		target		MapTarget in value
	param		query		GetMapQuery in value
	param		v		Float32 out array [COMPSIZE(target/query)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	121
	offset		267

GetMapiv(target, query, v)
	return		void
	param		target		MapTarget in value
	param		query		GetMapQuery in value
	param		v		Int32 out array [COMPSIZE(target/query)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	122
	offset		268

GetMaterialfv(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	123
	wglflags	small-data
	offset		269

GetMaterialiv(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	124
	wglflags	small-data
	offset		270

GetPixelMapfv(map, values)
	return		void
	param		map		PixelMap in value
	param		values		Float32 out array [COMPSIZE(map)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	125
	offset		271

GetPixelMapuiv(map, values)
	return		void
	param		map		PixelMap in value
	param		values		UInt32 out array [COMPSIZE(map)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	126
	offset		272

GetPixelMapusv(map, values)
	return		void
	param		map		PixelMap in value
	param		values		UInt16 out array [COMPSIZE(map)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	127
	offset		273

GetPolygonStipple(mask)
	return		void
	param		mask		UInt8 out array [COMPSIZE()]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	128
	wglflags	client-handcode server-handcode
	offset		274

GetTexEnvfv(target, pname, params)
	return		void
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	130
	wglflags	small-data
	offset		276

GetTexEnviv(target, pname, params)
	return		void
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	131
	wglflags	small-data
	offset		277

GetTexGendv(coord, pname, params)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Float64 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	132
	wglflags	small-data
	offset		278

GetTexGenfv(coord, pname, params)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	133
	wglflags	small-data
	offset		279

GetTexGeniv(coord, pname, params)
	return		void
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	134
	wglflags	small-data
	offset		280

IsList(list)
	return		Boolean
	param		list		List in value
	category	VERSION_1_0		   # old: state-req
	dlflags		notlistable
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxsingle	141
	offset		287

Frustum(left, right, bottom, top, zNear, zFar)
	return		void
	param		left		Float64 in value
	param		right		Float64 in value
	param		bottom		Float64 in value
	param		top		Float64 in value
	param		zNear		Float64 in value
	param		zFar		Float64 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	175
	offset		289

LoadIdentity()
	return		void
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	176
	offset		290

LoadMatrixf(m)
	return		void
	param		m		Float32 in array [16]
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	177
	offset		291

LoadMatrixd(m)
	return		void
	param		m		Float64 in array [16]
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	178
	offset		292

MatrixMode(mode)
	return		void
	param		mode		MatrixMode in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	179
	offset		293

MultMatrixf(m)
	return		void
	param		m		Float32 in array [16]
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	180
	offset		294

MultMatrixd(m)
	return		void
	param		m		Float64 in array [16]
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	181
	offset		295

Ortho(left, right, bottom, top, zNear, zFar)
	return		void
	param		left		Float64 in value
	param		right		Float64 in value
	param		bottom		Float64 in value
	param		top		Float64 in value
	param		zNear		Float64 in value
	param		zFar		Float64 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	182
	offset		296

PopMatrix()
	return		void
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	183
	offset		297

PushMatrix()
	return		void
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	184
	offset		298

Rotated(angle, x, y, z)
	return		void
	param		angle		Float64 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	185
	offset		299

Rotatef(angle, x, y, z)
	return		void
	param		angle		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	186
	offset		300

Scaled(x, y, z)
	return		void
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	187
	offset		301

Scalef(x, y, z)
	return		void
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	188
	offset		302

Translated(x, y, z)
	return		void
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	189
	offset		303

Translatef(x, y, z)
	return		void
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	VERSION_1_0		   # old: xform
	profile		compatibility
	version		1.0
	deprecated	3.1
	glxropcode	190
	offset		304

###############################################################################
###############################################################################
#
# OpenGL 1.1 commands
#
###############################################################################
###############################################################################

DrawArrays(mode, first, count)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in value
	param		count		SizeI in value
	category	VERSION_1_1
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	glxropcode	193
	offset		310

DrawElements(mode, count, type, indices)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	category	VERSION_1_1
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	offset		311

GetPointerv(pname, params)
	return		void
	param		pname		GetPointervPName in value
	param		params		VoidPointer out reference
	category	VERSION_1_1
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	offset		329

PolygonOffset(factor, units)
	return		void
	param		factor		Float32 in value
	param		units		Float32 in value
	category	VERSION_1_1
	version		1.1
	glxropcode	192
	offset		319

# Arguably TexelInternalFormat, not PixelInternalFormat
CopyTexImage1D(target, level, internalformat, x, y, width, border)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	category	VERSION_1_1
	version		1.1
	glxropcode	4119
	glxflags	EXT
	offset		323

# Arguably TexelInternalFormat, not PixelInternalFormat
CopyTexImage2D(target, level, internalformat, x, y, width, height, border)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	category	VERSION_1_1
	version		1.1
	glxropcode	4120
	glxflags	EXT
	offset		324

CopyTexSubImage1D(target, level, xoffset, x, y, width)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	VERSION_1_1
	version		1.1
	glxropcode	4121
	glxflags	EXT
	offset		325

CopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	VERSION_1_1
	version		1.1
	glxropcode	4122
	glxflags	EXT
	offset		326

TexSubImage1D(target, level, xoffset, width, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	VERSION_1_1
	dlflags		handcode
	glxflags	EXT client-handcode server-handcode
	version		1.1
	glxropcode	4099
	offset		332

TexSubImage2D(target, level, xoffset, yoffset, width, height, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	VERSION_1_1
	dlflags		handcode
	glxflags	EXT client-handcode server-handcode
	version		1.1
	glxropcode	4100
	offset		333

BindTexture(target, texture)
	return		void
	param		target		TextureTarget in value
	param		texture		Texture in value
	category	VERSION_1_1
	version		1.1
	glxropcode	4117
	glxflags	EXT
	offset		307

DeleteTextures(n, textures)
	return		void
	param		n		SizeI in value
	param		textures	Texture in array [n]
	category	VERSION_1_1
	dlflags		notlistable
	version		1.1
	glxsingle	144
	offset		327

GenTextures(n, textures)
	return		void
	param		n		SizeI in value
	param		textures	Texture out array [n]
	category	VERSION_1_1
	dlflags		notlistable
	version		1.1
	glxsingle	145
	offset		328

IsTexture(texture)
	return		Boolean
	param		texture		Texture in value
	category	VERSION_1_1
	dlflags		notlistable
	version		1.1
	glxsingle	146
	offset		330

###############################################################################
###############################################################################
#
# OpenGL 1.1 deprecated commands
#
###############################################################################
###############################################################################

ArrayElement(i)
	return		void
	param		i		Int32 in value
	category	VERSION_1_1
	profile		compatibility
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		306

ColorPointer(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		ColorPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		308

DisableClientState(array)
	return		void
	param		array		EnableCap in value
	category	VERSION_1_1
	profile		compatibility
	version		1.1
	deprecated	3.1
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	offset		309

EdgeFlagPointer(stride, pointer)
	return		void
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		312

EnableClientState(array)
	return		void
	param		array		EnableCap in value
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		313

IndexPointer(type, stride, pointer)
	return		void
	param		type		IndexPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		314

InterleavedArrays(format, stride, pointer)
	return		void
	param		format		InterleavedArrayFormat in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(format/stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		317

NormalPointer(type, stride, pointer)
	return		void
	param		type		NormalPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		318

TexCoordPointer(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		TexCoordPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		320

VertexPointer(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		VertexPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	VERSION_1_1
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	deprecated	3.1
	offset		321

AreTexturesResident(n, textures, residences)
	return		Boolean
	param		n		SizeI in value
	param		textures	Texture in array [n]
	param		residences	Boolean out array [n]
	category	VERSION_1_1
	profile		compatibility
	glxsingle	143
	dlflags		notlistable
	version		1.1
	deprecated	3.1
	offset		322

PrioritizeTextures(n, textures, priorities)
	return		void
	param		n		SizeI in value
	param		textures	Texture in array [n]
	param		priorities	Float32 in array [n]
	category	VERSION_1_1
	profile		compatibility
	version		1.1
	deprecated	3.1
	glxropcode	4118
	glxflags	EXT
	offset		331

Indexub(c)
	return		void
	param		c		ColorIndexValueUB in value
	category	VERSION_1_1
	profile		compatibility
	vectorequiv	Indexubv
	version		1.1
	offset		315

Indexubv(c)
	return		void
	param		c		ColorIndexValueUB in array [1]
	category	VERSION_1_1
	profile		compatibility
	version		1.1
	glxropcode	194
	offset		316

PopClientAttrib()
	return		void
	category	VERSION_1_1
	profile		compatibility
	version		1.1
	deprecated	3.1
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	offset		334

PushClientAttrib(mask)
	return		void
	param		mask		ClientAttribMask in value
	category	VERSION_1_1
	profile		compatibility
	version		1.1
	deprecated	3.1
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	offset		335

###############################################################################
###############################################################################
#
# OpenGL 1.2 commands
#
###############################################################################
###############################################################################

BlendColor(red, green, blue, alpha)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	param		alpha		ColorF in value
	category	VERSION_1_2
	glxflags	EXT
	version		1.2
	glxropcode	4096
	offset		336

BlendEquation(mode)
	return		void
	param		mode		BlendEquationMode in value
	category	VERSION_1_2
	glxflags	EXT
	version		1.2
	glxropcode	4097
	offset		337

DrawRangeElements(mode, start, end, count, type, indices)
	return		void
	param		mode		PrimitiveType in value
	param		start		UInt32 in value
	param		end		UInt32 in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	category	VERSION_1_2
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.2
	offset		338

# OpenGL 1.2 (EXT_texture3D) commands

# Arguably TexelInternalFormat, not PixelInternalFormat
TexImage3D(target, level, internalformat, width, height, depth, border, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureComponentCount in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	VERSION_1_2
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.2
	glxropcode	4114
	offset		371

TexSubImage3D(target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	VERSION_1_2
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.2
	glxropcode	4115
	offset		372

# OpenGL 1.2 (EXT_copy_texture) commands (specific to texture3D)

CopyTexSubImage3D(target, level, xoffset, yoffset, zoffset, x, y, width, height)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	VERSION_1_2
	glxflags	EXT
	version		1.2
	glxropcode	4123
	offset		373

###############################################################################
###############################################################################
#
# OpenGL 1.2 deprecated commands
#
###############################################################################
###############################################################################

# OpenGL 1.2 (SGI_color_table) commands

ColorTable(target, internalformat, width, format, type, table)
	return		void
	param		target		ColorTableTarget in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		table		Void in array [COMPSIZE(format/type/width)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.2
	deprecated	3.1
	glxropcode	2053
	offset		339

ColorTableParameterfv(target, pname, params)
	return		void
	param		target		ColorTableTarget in value
	param		pname		ColorTableParameterPName in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	2054
	offset		340

ColorTableParameteriv(target, pname, params)
	return		void
	param		target		ColorTableTarget in value
	param		pname		ColorTableParameterPName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	2055
	offset		341

CopyColorTable(target, internalformat, x, y, width)
	return		void
	param		target		ColorTableTarget in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	2056
	offset		342

GetColorTable(target, format, type, table)
	return		void
	param		target		ColorTableTarget in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		table		Void out array [COMPSIZE(target/format/type)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.2
	deprecated	3.1
	glxsingle	147
	offset		343

GetColorTableParameterfv(target, pname, params)
	return		void
	param		target		ColorTableTarget in value
	param		pname		GetColorTableParameterPName in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	148
	offset		344

GetColorTableParameteriv(target, pname, params)
	return		void
	param		target		ColorTableTarget in value
	param		pname		GetColorTableParameterPName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	149
	offset		345

# OpenGL 1.2 (EXT_color_subtable) commands

ColorSubTable(target, start, count, format, type, data)
	return		void
	param		target		ColorTableTarget in value
	param		start		SizeI in value
	param		count		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		data		Void in array [COMPSIZE(format/type/count)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		handcode
	glxflags	client-handcode server-handcode
	version		1.2
	deprecated	3.1
	glxropcode	195
	offset		346

CopyColorSubTable(target, start, x, y, width)
	return		void
	param		target		ColorTableTarget in value
	param		start		SizeI in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	VERSION_1_2
	profile		compatibility
	version		1.2
	deprecated	3.1
	glxropcode	196
	offset		347

# OpenGL 1.2 (EXT_convolution) commands

ConvolutionFilter1D(target, internalformat, width, format, type, image)
	return		void
	param		target		ConvolutionTarget in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		image		Void in array [COMPSIZE(format/type/width)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.2
	deprecated	3.1
	glxropcode	4101
	offset		348

ConvolutionFilter2D(target, internalformat, width, height, format, type, image)
	return		void
	param		target		ConvolutionTarget in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		image		Void in array [COMPSIZE(format/type/width/height)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.2
	deprecated	3.1
	glxropcode	4102
	offset		349

ConvolutionParameterf(target, pname, params)
	return		void
	param		target		ConvolutionTarget in value
	param		pname		ConvolutionParameter in value
	param		params		CheckedFloat32 in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4103
	offset		350

ConvolutionParameterfv(target, pname, params)
	return		void
	param		target		ConvolutionTarget in value
	param		pname		ConvolutionParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4104
	offset		351

ConvolutionParameteri(target, pname, params)
	return		void
	param		target		ConvolutionTarget in value
	param		pname		ConvolutionParameter in value
	param		params		CheckedInt32 in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4105
	offset		352

ConvolutionParameteriv(target, pname, params)
	return		void
	param		target		ConvolutionTarget in value
	param		pname		ConvolutionParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4106
	offset		353

CopyConvolutionFilter1D(target, internalformat, x, y, width)
	return		void
	param		target		ConvolutionTarget in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4107
	offset		354

CopyConvolutionFilter2D(target, internalformat, x, y, width, height)
	return		void
	param		target		ConvolutionTarget in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4108
	offset		355

GetConvolutionFilter(target, format, type, image)
	return		void
	param		target		ConvolutionTarget in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		image		Void out array [COMPSIZE(target/format/type)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.2
	deprecated	3.1
	glxsingle	150
	offset		356

GetConvolutionParameterfv(target, pname, params)
	return		void
	param		target		ConvolutionTarget in value
	param		pname		GetConvolutionParameterPName in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	151
	offset		357

GetConvolutionParameteriv(target, pname, params)
	return		void
	param		target		ConvolutionTarget in value
	param		pname		GetConvolutionParameterPName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	152
	offset		358

GetSeparableFilter(target, format, type, row, column, span)
	return		void
	param		target		SeparableTarget in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		row		Void out array [COMPSIZE(target/format/type)]
	param		column		Void out array [COMPSIZE(target/format/type)]
	param		span		Void out array [COMPSIZE(target/format/type)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.2
	deprecated	3.1
	glxsingle	153
	offset		359

SeparableFilter2D(target, internalformat, width, height, format, type, row, column)
	return		void
	param		target		SeparableTarget in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		row		Void in array [COMPSIZE(target/format/type/width)]
	param		column		Void in array [COMPSIZE(target/format/type/height)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.2
	deprecated	3.1
	glxropcode	4109
	offset		360

# OpenGL 1.2 (EXT_histogram) commands

GetHistogram(target, reset, format, type, values)
	return		void
	param		target		HistogramTarget in value
	param		reset		Boolean in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		values		Void out array [COMPSIZE(target/format/type)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.2
	deprecated	3.1
	glxsingle	154
	offset		361

GetHistogramParameterfv(target, pname, params)
	return		void
	param		target		HistogramTarget in value
	param		pname		GetHistogramParameterPName in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	155
	offset		362

GetHistogramParameteriv(target, pname, params)
	return		void
	param		target		HistogramTarget in value
	param		pname		GetHistogramParameterPName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	156
	offset		363

GetMinmax(target, reset, format, type, values)
	return		void
	param		target		MinmaxTarget in value
	param		reset		Boolean in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		values		Void out array [COMPSIZE(target/format/type)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.2
	deprecated	3.1
	glxsingle	157
	offset		364

GetMinmaxParameterfv(target, pname, params)
	return		void
	param		target		MinmaxTarget in value
	param		pname		GetMinmaxParameterPName in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	158
	offset		365

GetMinmaxParameteriv(target, pname, params)
	return		void
	param		target		MinmaxTarget in value
	param		pname		GetMinmaxParameterPName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_2
	profile		compatibility
	dlflags		notlistable
	version		1.2
	deprecated	3.1
	glxsingle	159
	offset		366

Histogram(target, width, internalformat, sink)
	return		void
	param		target		HistogramTarget in value
	param		width		SizeI in value
	param		internalformat	PixelInternalFormat in value
	param		sink		Boolean in value
	category	VERSION_1_2
	profile		compatibility
	dlflags		handcode
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4110
	offset		367

Minmax(target, internalformat, sink)
	return		void
	param		target		MinmaxTarget in value
	param		internalformat	PixelInternalFormat in value
	param		sink		Boolean in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4111
	offset		368

ResetHistogram(target)
	return		void
	param		target		HistogramTarget in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4112
	offset		369

ResetMinmax(target)
	return		void
	param		target		MinmaxTarget in value
	category	VERSION_1_2
	profile		compatibility
	glxflags	EXT
	version		1.2
	deprecated	3.1
	glxropcode	4113
	offset		370

###############################################################################
###############################################################################
#
# OpenGL 1.3 commands
#
###############################################################################
###############################################################################

# OpenGL 1.3 (ARB_multitexture) commands

ActiveTexture(texture)
	return		void
	param		texture		TextureUnit in value
	category	VERSION_1_3
	glxflags	ARB
	version		1.3
	glxropcode	197
	offset		374

# OpenGL 1.3 (ARB_multisample) commands

SampleCoverage(value, invert)
	return		void
	param		value		Float32 in value
	param		invert		Boolean in value
	category	VERSION_1_3
	glxflags	ARB
	version		1.3
	glxropcode	229
	offset		412

# OpenGL 1.3 (ARB_texture_compression) commands

# Arguably TexelInternalFormat, not PixelInternalFormat
CompressedTexImage3D(target, level, internalformat, width, height, depth, border, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	VERSION_1_3
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxropcode	216
	wglflags	client-handcode server-handcode
	offset		554

# Arguably TexelInternalFormat, not PixelInternalFormat
CompressedTexImage2D(target, level, internalformat, width, height, border, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	VERSION_1_3
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxropcode	215
	wglflags	client-handcode server-handcode
	offset		555

# Arguably TexelInternalFormat, not PixelInternalFormat
CompressedTexImage1D(target, level, internalformat, width, border, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	VERSION_1_3
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxropcode	214
	wglflags	client-handcode server-handcode
	offset		556

CompressedTexSubImage3D(target, level, xoffset, yoffset, zoffset, width, height, depth, format, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	VERSION_1_3
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxropcode	219
	wglflags	client-handcode server-handcode
	offset		557

CompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	VERSION_1_3
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxropcode	218
	wglflags	client-handcode server-handcode
	offset		558

CompressedTexSubImage1D(target, level, xoffset, width, format, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	VERSION_1_3
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxropcode	217
	wglflags	client-handcode server-handcode
	offset		559

GetCompressedTexImage(target, level, img)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		img		CompressedTextureARB out array [COMPSIZE(target/level)]
	category	VERSION_1_3
	dlflags		notlistable
	glxflags	ARB client-handcode server-handcode
	version		1.3
	glxsingle	160
	wglflags	client-handcode server-handcode
	offset		560

###############################################################################
###############################################################################
#
# OpenGL 1.3 deprecated commands
#
###############################################################################
###############################################################################

ClientActiveTexture(texture)
	return		void
	param		texture		TextureUnit in value
	category	VERSION_1_3
	profile		compatibility
	dlflags		notlistable
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.3
	deprecated	3.1
	offset		375

MultiTexCoord1d(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord1dv
	offset		376

MultiTexCoord1dv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [1]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	198
	offset		377

MultiTexCoord1f(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord1fv
	offset		378

MultiTexCoord1fv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [1]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	199
	offset		379

MultiTexCoord1i(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord1iv
	offset		380

MultiTexCoord1iv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [1]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	200
	offset		381

MultiTexCoord1s(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord1sv
	offset		382

MultiTexCoord1sv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [1]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	201
	offset		383

MultiTexCoord2d(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	param		t		CoordD in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord2dv
	offset		384

MultiTexCoord2dv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [2]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	202
	offset		385

MultiTexCoord2f(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	param		t		CoordF in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord2fv
	offset		386

MultiTexCoord2fv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [2]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	203
	offset		387

MultiTexCoord2i(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	param		t		CoordI in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord2iv
	offset		388

MultiTexCoord2iv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [2]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	204
	offset		389

MultiTexCoord2s(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	param		t		CoordS in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord2sv
	offset		390

MultiTexCoord2sv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [2]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	205
	offset		391

MultiTexCoord3d(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	param		t		CoordD in value
	param		r		CoordD in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord3dv
	offset		392

MultiTexCoord3dv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [3]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	206
	offset		393

MultiTexCoord3f(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	param		t		CoordF in value
	param		r		CoordF in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord3fv
	offset		394

MultiTexCoord3fv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [3]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	207
	offset		395

MultiTexCoord3i(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	param		t		CoordI in value
	param		r		CoordI in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord3iv
	offset		396

MultiTexCoord3iv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [3]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	208
	offset		397

MultiTexCoord3s(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	param		t		CoordS in value
	param		r		CoordS in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord3sv
	offset		398

MultiTexCoord3sv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [3]
	category	VERSION_1_3
	profile		compatibility
	version		1.3
	deprecated	3.1
	glxflags	ARB
	glxropcode	209
	offset		399

MultiTexCoord4d(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	param		t		CoordD in value
	param		r		CoordD in value
	param		q		CoordD in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord4dv
	offset		400

MultiTexCoord4dv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [4]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	210
	offset		401

MultiTexCoord4f(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	param		t		CoordF in value
	param		r		CoordF in value
	param		q		CoordF in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord4fv
	offset		402

MultiTexCoord4fv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [4]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	211
	offset		403

MultiTexCoord4i(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	param		t		CoordI in value
	param		r		CoordI in value
	param		q		CoordI in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord4iv
	offset		404

MultiTexCoord4iv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [4]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	212
	offset		405

MultiTexCoord4s(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	param		t		CoordS in value
	param		r		CoordS in value
	param		q		CoordS in value
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	vectorequiv	MultiTexCoord4sv
	offset		406

MultiTexCoord4sv(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [4]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB
	version		1.3
	deprecated	3.1
	glxropcode	213
	offset		407

# OpenGL 1.3 (ARB_transpose_matrix) commands

LoadTransposeMatrixf(m)
	return		void
	param		m		Float32 in array [16]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.3
	deprecated	3.1
	offset		408

LoadTransposeMatrixd(m)
	return		void
	param		m		Float64 in array [16]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.3
	deprecated	3.1
	offset		409

MultTransposeMatrixf(m)
	return		void
	param		m		Float32 in array [16]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.3
	deprecated	3.1
	offset		410

MultTransposeMatrixd(m)
	return		void
	param		m		Float64 in array [16]
	category	VERSION_1_3
	profile		compatibility
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.3
	deprecated	3.1
	offset		411

###############################################################################
###############################################################################
#
# OpenGL 1.4 commands
#
###############################################################################
###############################################################################

# OpenGL 1.4 (EXT_blend_func_separate) commands

BlendFuncSeparate(sfactorRGB, dfactorRGB, sfactorAlpha, dfactorAlpha)
	return		void
	param		sfactorRGB	BlendFuncSeparateParameterEXT in value
	param		dfactorRGB	BlendFuncSeparateParameterEXT in value
	param		sfactorAlpha	BlendFuncSeparateParameterEXT in value
	param		dfactorAlpha	BlendFuncSeparateParameterEXT in value
	category	VERSION_1_4
	glxropcode	4134
	version		1.4
	extension
	offset		537

# OpenGL 1.4 (EXT_multi_draw_arrays) commands

# first and count are really 'in'
MultiDrawArrays(mode, first, count, drawcount)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in array [COMPSIZE(count)]
	param		count		SizeI in array [COMPSIZE(drawcount)]
	param		drawcount	SizeI in value
	category	VERSION_1_4
	version		1.4
	glxropcode	?
	offset		644

MultiDrawElements(mode, count, type, indices, drawcount)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in array [COMPSIZE(drawcount)]
	param		type		DrawElementsType in value
	param		indices		ConstVoidPointer in array [COMPSIZE(drawcount)]
	param		drawcount	SizeI in value
	category	VERSION_1_4
	version		1.4
	glxropcode	?
	offset		645

# OpenGL 1.4 (ARB_point_parameters, NV_point_sprite) commands

PointParameterf(pname, param)
	return		void
	param		pname		PointParameterNameARB in value
	param		param		CheckedFloat32 in value
	category	VERSION_1_4
	version		1.4
	glxropcode	2065
	extension
	offset		458

PointParameterfv(pname, params)
	return		void
	param		pname		PointParameterNameARB in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	VERSION_1_4
	version		1.4
	glxropcode	2066
	extension
	offset		459

PointParameteri(pname, param)
	return		void
	param		pname		PointParameterNameARB in value
	param		param		Int32 in value
	category	VERSION_1_4
	version		1.4
	extension	soft WINSOFT NV20
	glxropcode	4221
	offset		642

PointParameteriv(pname, params)
	return		void
	param		pname		PointParameterNameARB in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	VERSION_1_4
	version		1.4
	extension	soft WINSOFT NV20
	glxropcode	4222re
	offset		643

###############################################################################
###############################################################################
#
# OpenGL 1.4 deprecated commands
#
###############################################################################
###############################################################################

# OpenGL 1.4 (EXT_fog_coord) commands

FogCoordf(coord)
	return		void
	param		coord		CoordF in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	FogCoordfv
	version		1.4
	deprecated	3.1
	offset		545

FogCoordfv(coord)
	return		void
	param		coord		CoordF in array [1]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4124
	offset		546

FogCoordd(coord)
	return		void
	param		coord		CoordD in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	FogCoorddv
	version		1.4
	deprecated	3.1
	offset		547

FogCoorddv(coord)
	return		void
	param		coord		CoordD in array [1]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4125
	offset		548

FogCoordPointer(type, stride, pointer)
	return		void
	param		type		FogPointerTypeEXT in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	VERSION_1_4
	profile		compatibility
	dlflags		notlistable
	version		1.4
	deprecated	3.1
	glxflags	client-handcode server-handcode
	offset		549

# OpenGL 1.4 (EXT_secondary_color) commands

SecondaryColor3b(red, green, blue)
	return		void
	param		red		ColorB in value
	param		green		ColorB in value
	param		blue		ColorB in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3bv
	version		1.4
	deprecated	3.1
	offset		561

SecondaryColor3bv(v)
	return		void
	param		v		ColorB in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4126
	offset		562

SecondaryColor3d(red, green, blue)
	return		void
	param		red		ColorD in value
	param		green		ColorD in value
	param		blue		ColorD in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3dv
	version		1.4
	deprecated	3.1
	offset		563

SecondaryColor3dv(v)
	return		void
	param		v		ColorD in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4130
	offset		564

SecondaryColor3f(red, green, blue)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3fv
	version		1.4
	deprecated	3.1
	offset		565

SecondaryColor3fv(v)
	return		void
	param		v		ColorF in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4129
	offset		566

SecondaryColor3i(red, green, blue)
	return		void
	param		red		ColorI in value
	param		green		ColorI in value
	param		blue		ColorI in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3iv
	version		1.4
	deprecated	3.1
	offset		567

SecondaryColor3iv(v)
	return		void
	param		v		ColorI in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4128
	offset		568

SecondaryColor3s(red, green, blue)
	return		void
	param		red		ColorS in value
	param		green		ColorS in value
	param		blue		ColorS in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3sv
	version		1.4
	deprecated	3.1
	offset		569

SecondaryColor3sv(v)
	return		void
	param		v		ColorS in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4127
	offset		570

SecondaryColor3ub(red, green, blue)
	return		void
	param		red		ColorUB in value
	param		green		ColorUB in value
	param		blue		ColorUB in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3ubv
	version		1.4
	deprecated	3.1
	offset		571

SecondaryColor3ubv(v)
	return		void
	param		v		ColorUB in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4131
	offset		572

SecondaryColor3ui(red, green, blue)
	return		void
	param		red		ColorUI in value
	param		green		ColorUI in value
	param		blue		ColorUI in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3uiv
	version		1.4
	deprecated	3.1
	offset		573

SecondaryColor3uiv(v)
	return		void
	param		v		ColorUI in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4133
	offset		574

SecondaryColor3us(red, green, blue)
	return		void
	param		red		ColorUS in value
	param		green		ColorUS in value
	param		blue		ColorUS in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	SecondaryColor3usv
	version		1.4
	deprecated	3.1
	offset		575

SecondaryColor3usv(v)
	return		void
	param		v		ColorUS in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	4132
	offset		576

SecondaryColorPointer(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		ColorPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	VERSION_1_4
	profile		compatibility
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	version		1.4
	deprecated	3.1
	extension
	offset		577

# OpenGL 1.4 (ARB_window_pos) commands
# Note: all WindowPos* entry points use glxropcode ropcode 230, with 3 float parameters

WindowPos2d(x, y)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos2dv
	version		1.4
	deprecated	3.1
	offset		513

WindowPos2dv(v)
	return		void
	param		v		CoordD in array [2]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		514

WindowPos2f(x, y)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos2fv
	version		1.4
	deprecated	3.1
	offset		515

WindowPos2fv(v)
	return		void
	param		v		CoordF in array [2]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		516

WindowPos2i(x, y)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos2iv
	version		1.4
	deprecated	3.1
	offset		517

WindowPos2iv(v)
	return		void
	param		v		CoordI in array [2]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		518

WindowPos2s(x, y)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos2sv
	version		1.4
	deprecated	3.1
	offset		519

WindowPos2sv(v)
	return		void
	param		v		CoordS in array [2]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		520

WindowPos3d(x, y, z)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	vectorequiv	WindowPos3dv
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	offset		521

WindowPos3dv(v)
	return		void
	param		v		CoordD in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		522

WindowPos3f(x, y, z)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos3fv
	version		1.4
	deprecated	3.1
	offset		523

WindowPos3fv(v)
	return		void
	param		v		CoordF in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		524

WindowPos3i(x, y, z)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos3iv
	version		1.4
	deprecated	3.1
	offset		525

WindowPos3iv(v)
	return		void
	param		v		CoordI in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		526

WindowPos3s(x, y, z)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	category	VERSION_1_4
	profile		compatibility
	vectorequiv	WindowPos3sv
	version		1.4
	deprecated	3.1
	offset		527

WindowPos3sv(v)
	return		void
	param		v		CoordS in array [3]
	category	VERSION_1_4
	profile		compatibility
	version		1.4
	deprecated	3.1
	glxropcode	230
	glxflags	client-handcode server-handcode
	offset		528

###############################################################################
###############################################################################
#
# OpenGL 1.5 commands
#
###############################################################################
###############################################################################

# OpenGL 1.5 (ARB_occlusion_query) commands

GenQueries(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 out array [n]
	category	VERSION_1_5
	version		1.5
	extension
	glxsingle	162
	glxflags	ignore
	offset		700

DeleteQueries(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 in array [n]
	category	VERSION_1_5
	version		1.5
	extension
	glxsingle	161
	glxflags	ignore
	offset		701

IsQuery(id)
	return		Boolean
	param		id		UInt32 in value
	category	VERSION_1_5
	version		1.5
	extension
	glxsingle	163
	glxflags	ignore
	offset		702

BeginQuery(target, id)
	return		void
	param		target		GLenum in value
	param		id		UInt32 in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	231
	glxflags	ignore
	offset		703

EndQuery(target)
	return		void
	param		target		GLenum in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	232
	glxflags	ignore
	offset		704

GetQueryiv(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	VERSION_1_5
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	164
	glxflags	ignore
	offset		705

GetQueryObjectiv(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	VERSION_1_5
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	165
	glxflags	ignore
	offset		706

GetQueryObjectuiv(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt32 out array [pname]
	category	VERSION_1_5
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	166
	glxflags	ignore
	offset		707

# OpenGL 1.5 (ARB_vertex_buffer_object) commands

BindBuffer(target, buffer)
	return		void
	param		target		BufferTargetARB in value
	param		buffer		UInt32 in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		688

DeleteBuffers(n, buffers)
	return		void
	param		n		SizeI in value
	param		buffers		ConstUInt32 in array [n]
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		691

GenBuffers(n, buffers)
	return		void
	param		n		SizeI in value
	param		buffers		UInt32 out array [n]
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		692

IsBuffer(buffer)
	return		Boolean
	param		buffer		UInt32 in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		696

BufferData(target, size, data, usage)
	return		void
	param		target		BufferTargetARB in value
	param		size		BufferSize in value
	param		data		ConstVoid in array [size]
	param		usage		BufferUsageARB in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		689

BufferSubData(target, offset, size, data)
	return		void
	param		target		BufferTargetARB in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	param		data		ConstVoid in array [size]
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		690

GetBufferSubData(target, offset, size, data)
	return		void
	param		target		BufferTargetARB in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	param		data		Void out array [size]
	category	VERSION_1_5
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	?
	glxflags	ignore
	offset		695

MapBuffer(target, access)
	return		VoidPointer
	param		target		BufferTargetARB in value
	param		access		BufferAccessARB in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		697

UnmapBuffer(target)
	return		Boolean
	param		target		BufferTargetARB in value
	category	VERSION_1_5
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		698

GetBufferParameteriv(target, pname, params)
	return		void
	param		target		BufferTargetARB in value
	param		pname		BufferPNameARB in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_1_5
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	?
	glxflags	ignore
	offset		693

GetBufferPointerv(target, pname, params)
	return		void
	param		target		BufferTargetARB in value
	param		pname		BufferPointerNameARB in value
	param		params		VoidPointer out array [1]
	category	VERSION_1_5
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	?
	glxflags	ignore
	offset		694

# OpenGL 1.5 (EXT_shadow_funcs) commands - none


###############################################################################
###############################################################################
#
# OpenGL 2.0 commands
#
###############################################################################
###############################################################################

# OpenGL 2.0 (EXT_blend_equation_separate) commands

BlendEquationSeparate(modeRGB, modeAlpha)
	return		void
	param		modeRGB		BlendEquationModeEXT in value
	param		modeAlpha	BlendEquationModeEXT in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	4228

# OpenGL 2.0 (ARB_draw_buffers) commands

DrawBuffers(n, bufs)
	return		void
	param		n		SizeI in value
	param		bufs		DrawBufferModeATI in array [n]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	233
	glxflags	ignore
	offset		?

# OpenGL 2.0 (ARB_stencil_two_side) commands

StencilOpSeparate(face, sfail, dpfail, dppass)
	return		void
	param		face		StencilFaceDirection in value
	param		sfail		StencilOp in value
	param		dpfail		StencilOp in value
	param		dppass		StencilOp in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

StencilFuncSeparate(face, func, ref, mask)
	return		void
	param		face		StencilFaceDirection in value
	param		func		StencilFunction in value
	param		ref		StencilValue in value
	param		mask		MaskedStencilValue in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

StencilMaskSeparate(face, mask)
	return		void
	param		face		StencilFaceDirection in value
	param		mask		MaskedStencilValue in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# OpenGL 2.0 (ARB_shader_objects / ARB_vertex_shader / ARB_fragment_shader) commands

AttachShader(program, shader)
	return		void
	param		program		UInt32 in value
	param		shader		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindAttribLocation(program, index, name)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		name		Char in array []
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

CompileShader(shader)
	return		void
	param		shader		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

CreateProgram()
	return		UInt32
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

CreateShader(type)
	return		UInt32
	param		type		GLenum in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteProgram(program)
	return		void
	param		program		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxsingle	202
	offset		?

DeleteShader(shader)
	return		void
	param		shader		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxsingle	195
	offset		?

DetachShader(program, shader)
	return		void
	param		program		UInt32 in value
	param		shader		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DisableVertexAttribArray(index)
	return		void
	param		index		UInt32 in value
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		666

EnableVertexAttribArray(index)
	return		void
	param		index		UInt32 in value
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		665

GetActiveAttrib(program, index, bufSize, length, size, type, name)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		size		Int32 out array [1]
	param		type		GLenum out array [1]
	param		name		Char out array []
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveUniform(program, index, bufSize, length, size, type, name)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		size		Int32 out array [1]
	param		type		GLenum out array [1]
	param		name		Char out array []
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetAttachedShaders(program, maxCount, count, obj)
	return		void
	param		program		UInt32 in value
	param		maxCount	SizeI in value
	param		count		SizeI out array [1]
	param		obj		UInt32 out array [count]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetAttribLocation(program, name)
	return		Int32
	param		program		UInt32 in value
	param		name		Char in array []
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramiv(program, pname, params)
	return		void
	param		program		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	199
	offset		?

GetProgramInfoLog(program, bufSize, length, infoLog)
	return		void
	param		program		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		infoLog		Char out array [length]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	201
	offset		?

GetShaderiv(shader, pname, params)
	return		void
	param		shader		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	198
	offset		?

GetShaderInfoLog(shader, bufSize, length, infoLog)
	return		void
	param		shader		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		infoLog		Char out array [length]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	200
	offset		?

GetShaderSource(shader, bufSize, length, source)
	return		void
	param		shader		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		source		Char out array [length]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetUniformLocation(program, name)
	return		Int32
	param		program		UInt32 in value
	param		name		Char in array []
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetUniformfv(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		Float32 out array [COMPSIZE(location)]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetUniformiv(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		Int32 out array [COMPSIZE(location)]
	category	VERSION_2_0
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVertexAttribdv(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPropertyARB in value
	param		params		Float64 out array [4]
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxvendorpriv	1301
	offset		588

GetVertexAttribfv(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPropertyARB in value
	param		params		Float32 out array [4]
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxvendorpriv	1302
	offset		589

GetVertexAttribiv(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPropertyARB in value
	param		params		Int32 out array [4]
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxvendorpriv	1303
	offset		590

GetVertexAttribPointerv(index, pname, pointer)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPointerPropertyARB in value
	param		pointer		VoidPointer out array [1]
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		591

IsProgram(program)
	return		Boolean
	param		program		UInt32 in value
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxsingle	197
	offset		592

IsShader(shader)
	return		Boolean
	param		shader		UInt32 in value
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxsingle	196
	offset		?

LinkProgram(program)
	return		void
	param		program		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ShaderSource(shader, count, string, length)
	return		void
	param		shader		UInt32 in value
	param		count		SizeI in value
	param		string		ConstCharPointer in array [count]
	param		length		Int32 in array [1]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UseProgram(program)
	return		void
	param		program		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1f(location, v0)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2f(location, v0, v1)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3f(location, v0, v1, v2)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4f(location, v0, v1, v2, v3)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	param		v3		Float32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1i(location, v0)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2i(location, v0, v1)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3i(location, v0, v1, v2)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4i(location, v0, v1, v2, v3)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	param		v3		Int32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1fv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2fv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3fv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4fv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1iv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2iv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3iv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4iv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix2fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix3fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix4fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ValidateProgram(program)
	return		void
	param		program		UInt32 in value
	category	VERSION_2_0
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttrib1d(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib1dv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		603

VertexAttrib1dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [1]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4197
	offset		604

VertexAttrib1f(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib1fv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		605

VertexAttrib1fv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [1]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4193
	offset		606

VertexAttrib1s(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib1sv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		607

VertexAttrib1sv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [1]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4189
	offset		608

VertexAttrib2d(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib2dv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		609

VertexAttrib2dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [2]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4198
	offset		610

VertexAttrib2f(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib2fv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		611

VertexAttrib2fv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [2]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4194
	offset		612

VertexAttrib2s(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib2sv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		613

VertexAttrib2sv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [2]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4190
	offset		614

VertexAttrib3d(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib3dv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		615

VertexAttrib3dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [3]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4199
	offset		616

VertexAttrib3f(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib3fv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		617

VertexAttrib3fv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [3]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4195
	offset		618

VertexAttrib3s(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib3sv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		619

VertexAttrib3sv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [3]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4191
	offset		620

VertexAttrib4Nbv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int8 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		659

VertexAttrib4Niv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		661

VertexAttrib4Nsv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		660

VertexAttrib4Nub(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		UInt8 in value
	param		y		UInt8 in value
	param		z		UInt8 in value
	param		w		UInt8 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		627

VertexAttrib4Nubv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt8 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxropcode	4201
	offset		628

VertexAttrib4Nuiv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		663

VertexAttrib4Nusv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt16 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		662

VertexAttrib4bv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int8 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		654

VertexAttrib4d(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib4dv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		621

VertexAttrib4dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4200
	offset		622

VertexAttrib4f(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib4fv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		623

VertexAttrib4fv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxropcode	4196
	offset		624

VertexAttrib4iv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		655

VertexAttrib4s(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	param		w		Int16 in value
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	vectorequiv	VertexAttrib4sv
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		625

VertexAttrib4sv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxropcode	4192
	offset		626

VertexAttrib4ubv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt8 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		656

VertexAttrib4uiv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		658

VertexAttrib4usv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt16 in array [4]
	category	VERSION_2_0
	version		2.0
	deprecated	3.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		657

VertexAttribPointer(index, size, type, normalized, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		VertexAttribPointerTypeARB in value
	param		normalized	Boolean in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	dlflags		notlistable
	category	VERSION_2_0
	version		2.0
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		664


###############################################################################
###############################################################################
#
# OpenGL 2.1 commands
#
###############################################################################
###############################################################################

# OpenGL 2.1 (ARB_pixel_buffer_object) commands - none

# OpenGL 2.1 (EXT_texture_sRGB) commands - none

# New commands in OpenGL 2.1

UniformMatrix2x3fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [6]
	category	VERSION_2_1
	version		2.1
	extension
	glxropcode	305
	glxflags	ignore
	offset		?

UniformMatrix3x2fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [6]
	category	VERSION_2_1
	version		2.1
	extension
	glxropcode	306
	offset		?

UniformMatrix2x4fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [8]
	category	VERSION_2_1
	version		2.1
	extension
	glxropcode	307
	offset		?

UniformMatrix4x2fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [8]
	category	VERSION_2_1
	version		2.1
	extension
	glxropcode	308
	offset		?

UniformMatrix3x4fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [12]
	category	VERSION_2_1
	version		2.1
	extension
	glxropcode	309
	offset		?

UniformMatrix4x3fv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [12]
	category	VERSION_2_1
	version		2.1
	extension
	glxropcode	310
	offset		?

###############################################################################
###############################################################################
#
# OpenGL 3.0 commands
#
###############################################################################
###############################################################################

# OpenGL 3.0 (EXT_draw_buffers2) commands

ColorMaski(index, r, g, b, a)
	return		void
	param		index		UInt32 in value
	param		r		Boolean in value
	param		g		Boolean in value
	param		b		Boolean in value
	param		a		Boolean in value
	category	VERSION_3_0
	version		3.0
	extension
	glxflags	ignore
	glfflags	ignore

GetBooleani_v(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Boolean out array [COMPSIZE(target)]
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

GetIntegeri_v(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Int32 out array [COMPSIZE(target)]
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

Enablei(target, index)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glxflags	ignore
	glfflags	ignore

Disablei(target, index)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glxflags	ignore
	glfflags	ignore

IsEnabledi(target, index)
	return		Boolean
	param		target		GLenum in value
	param		index		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

# OpenGL 3.0 (EXT_transform_feedback) commands

BeginTransformFeedback(primitiveMode)
	return		void
	param		primitiveMode	GLenum in value
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

EndTransformFeedback()
	return		void
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

BindBufferRange(target, index, buffer, offset, size)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

BindBufferBase(target, index, buffer)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

TransformFeedbackVaryings(program, count, varyings, bufferMode)
	return		void
	param		program		UInt32 in value
	param		count		SizeI in value
	param		varyings	ConstCharPointer in array [count]
	param		bufferMode	GLenum in value
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

GetTransformFeedbackVarying(program, index, bufSize, length, size, type, name)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		size		SizeI out array [1]
	param		type		GLenum out array [1]
	param		name		Char out array [COMPSIZE(length)]
	category	VERSION_3_0
	dlflags		notlistable
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

ClampColor(target, clamp)
	return		void
	param		target		ClampColorTargetARB in value
	param		clamp		ClampColorModeARB in value
	category	VERSION_3_0
	version		3.0
	extension
	glxropcode	234
	glxflags	ignore
	offset		?

BeginConditionalRender(id, mode)
	return		void
	param		id		UInt32 in value
	param		mode		TypeEnum in value
	category	VERSION_3_0
	version		3.0
	glfflags	ignore
	glxflags	ignore

EndConditionalRender()
	return		void
	category	VERSION_3_0
	version		3.0
	glfflags	ignore
	glxflags	ignore

VertexAttribIPointer(index, size, type, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		VertexAttribEnum in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	VERSION_3_0
	version		3.0
	dlflags		notlistable
	extension
	glfflags	ignore
	glxflags	ignore

GetVertexAttribIiv(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnum in value
	param		params		Int32 out array [1]
	category	VERSION_3_0
	version		3.0
	dlflags		notlistable
	extension
	glfflags	ignore
	glxflags	ignore

GetVertexAttribIuiv(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnum in value
	param		params		UInt32 out array [1]
	category	VERSION_3_0
	version		3.0
	dlflags		notlistable
	extension
	glfflags	ignore
	glxflags	ignore

# OpenGL 3.0 (NV_vertex_program4) commands

VertexAttribI1i(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI1iv
	glxvectorequiv	VertexAttribI1iv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI2i(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI2iv
	glxvectorequiv	VertexAttribI2iv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI3i(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI3iv
	glxvectorequiv	VertexAttribI3iv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4i(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	param		w		Int32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI4iv
	glxvectorequiv	VertexAttribI4iv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI1ui(index, x)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI1uiv
	glxvectorequiv	VertexAttribI1uiv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI2ui(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI2uiv
	glxvectorequiv	VertexAttribI2uiv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI3ui(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI3uiv
	glxvectorequiv	VertexAttribI3uiv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4ui(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	param		w		UInt32 in value
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	vectorequiv	VertexAttribI4uiv
	glxvectorequiv	VertexAttribI4uiv
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI1iv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [1]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI2iv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [2]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI3iv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [3]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4iv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI1uiv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [1]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI2uiv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [2]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI3uiv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [3]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4uiv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [4]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4bv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int8 in array [4]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4sv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4ubv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt8 in array [4]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

VertexAttribI4usv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt16 in array [4]
	category	VERSION_3_0
	version		3.0
	deprecated	3.1
	beginend	allow-inside
	extension
	glfflags	ignore
	glxflags	ignore

# OpenGL 3.0 (EXT_gpu_shader4) commands

GetUniformuiv(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		UInt32 out array [COMPSIZE(program/location)]
	category	VERSION_3_0
	dlflags		notlistable
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

BindFragDataLocation(program, color, name)
	return		void
	param		program		UInt32 in value
	param		color		UInt32 in value
	param		name		Char in array [COMPSIZE(name)]
	category	VERSION_3_0
	dlflags		notlistable
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

GetFragDataLocation(program, name)
	return		Int32
	param		program		UInt32 in value
	param		name		Char in array [COMPSIZE(name)]
	category	VERSION_3_0
	dlflags		notlistable
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform1ui(location, v0)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform2ui(location, v0, v1)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform3ui(location, v0, v1, v2)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform4ui(location, v0, v1, v2, v3)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	param		v3		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform1uiv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform2uiv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*2]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform3uiv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*3]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

Uniform4uiv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*4]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

# OpenGL 3.0 (EXT_texture_integer) commands

TexParameterIiv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

TexParameterIuiv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		UInt32 in array [COMPSIZE(pname)]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

GetTexParameterIiv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	VERSION_3_0
	dlflags		notlistable
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

GetTexParameterIuiv(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	category	VERSION_3_0
	dlflags		notlistable
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

# New commands in OpenGL 3.0

ClearBufferiv(buffer, drawbuffer, value)
	return		void
	param		buffer		GLenum in value
	param		drawbuffer	DrawBufferName in value
	param		value		Int32 in array [COMPSIZE(buffer)]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

ClearBufferuiv(buffer, drawbuffer, value)
	return		void
	param		buffer		GLenum in value
	param		drawbuffer	DrawBufferName in value
	param		value		UInt32 in array [COMPSIZE(buffer)]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

ClearBufferfv(buffer, drawbuffer, value)
	return		void
	param		buffer		GLenum in value
	param		drawbuffer	DrawBufferName in value
	param		value		Float32 in array [COMPSIZE(buffer)]
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

ClearBufferfi(buffer, drawbuffer, depth, stencil)
	return		void
	param		buffer		GLenum in value
	param		drawbuffer	DrawBufferName in value
	param		depth		Float32 in value
	param		stencil		Int32 in value
	category	VERSION_3_0
	version		3.0
	extension
	glfflags	ignore
	glxflags	ignore

GetStringi(name, index)
	return		String
	param		name		GLenum in value
	param		index		UInt32 in value
	category	VERSION_3_0
	version		3.0
	extension
	dlflags		notlistable
	glxflags	client-handcode server-handcode
	glfflags	ignore
	glxsingle	?

passthru: /* OpenGL 3.0 also reuses entry points from these extensions: */
passthru: /* ARB_framebuffer_object */
passthru: /* ARB_map_buffer_range */
passthru: /* ARB_vertex_array_object */

###############################################################################
###############################################################################
#
# OpenGL 3.0 deprecated commands
#
###############################################################################
###############################################################################

# (none - VertexAttribI* were moved back into non-deprecated)


###############################################################################
###############################################################################
#
# OpenGL 3.1 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 3.1 - none

# OpenGL 3.1 (ARB_draw_instanced) commands

DrawArraysInstanced(mode, first, count, instancecount)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in value
	param		count		SizeI in value
	param		instancecount	SizeI in value
	category	VERSION_3_1
	version		3.1
	extension
	dlflags		notlistable
	vectorequiv	ArrayElement
	glfflags	ignore
	glxflags	ignore

DrawElementsInstanced(mode, count, type, indices, instancecount)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	param		instancecount	SizeI in value
	category	VERSION_3_1
	version		3.1
	extension
	dlflags		notlistable
	vectorequiv	ArrayElement
	glfflags	ignore
	glxflags	ignore

# OpenGL 3.1 (ARB_texture_buffer_object) commands

TexBuffer(target, internalformat, buffer)
	return		void
	param		target		TextureTarget in value
	param		internalformat	GLenum in value
	param		buffer		UInt32 in value
	category	VERSION_3_1
	version		3.1
	extension
	glfflags	ignore
	glxflags	ignore

# OpenGL 3.1 (ARB_texture_rectangle) commands - none

# OpenGL 3.1 (SNORM texture) commands - none

# OpenGL 3.1 (NV_primitive_restart) commands
# This is *not* an alias of PrimitiveRestartIndexNV, since it sets
# server instead of client state.

PrimitiveRestartIndex(index)
	return		void
	param		index		UInt32 in value
	category	VERSION_3_1
	version		3.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

passthru: /* OpenGL 3.1 also reuses entry points from these extensions: */
passthru: /* ARB_copy_buffer */
passthru: /* ARB_uniform_buffer_object */


###############################################################################
###############################################################################
#
# OpenGL 3.2 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 3.2

GetInteger64i_v(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Int64 out array [COMPSIZE(target)]
	category	VERSION_3_2
	version		3.2
	extension
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore


GetBufferParameteri64v(target, pname, params)
	return		void
	param		target		BufferTargetARB in value
	param		pname		BufferPNameARB in value
	param		params		Int64 out array [COMPSIZE(pname)]
	category	VERSION_3_2
	dlflags		notlistable
	version		3.2
	extension
	glxsingle	?
	glxflags	ignore

# OpenGL 3.2 (ARB_depth_clamp) commands - none
# OpenGL 3.2 (ARB_fragment_coord_conventions) commands - none

# OpenGL 3.2 (ARB_geometry_shader4) commands
# ProgramParameteriARB was NOT promoted to core 3.2, but
# IS part of core 4.1 through other ARB extensions.

FramebufferTexture(target, attachment, texture, level)
	return		void
	param		target		GLenum in value
	param		attachment	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	VERSION_3_2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# FramebufferTextureLayer already declared in ARB_framebuffer_object
# FramebufferTextureLayer(target, attachment, texture, level, layer)

# Not promoted to the core along with the rest
# FramebufferTextureFace(target, attachment, texture, level, face)

# OpenGL 3.2  (ARB_seamless_cube_map) commands - none
# OpenGL 3.2  (ARB_vertex_array_bgra) commands - none

passthru: /* OpenGL 3.2 also reuses entry points from these extensions: */
passthru: /* ARB_draw_elements_base_vertex */
passthru: /* ARB_provoking_vertex */
passthru: /* ARB_sync */
passthru: /* ARB_texture_multisample */


###############################################################################
###############################################################################
#
# OpenGL 3.3 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 3.3

# OpenGL 3.3 (ARB_instanced_arrays) commands

VertexAttribDivisor(index, divisor)
	return		void
	param		index		UInt32 in value
	param		divisor		UInt32 in value
	category	VERSION_3_3
	version		1.1
	extension
	glfflags	ignore
	glxflags	ignore

passthru: /* OpenGL 3.3 also reuses entry points from these extensions: */
passthru: /* ARB_blend_func_extended */
passthru: /* ARB_sampler_objects */
passthru: /* ARB_explicit_attrib_location, but it has none */
passthru: /* ARB_occlusion_query2 (no entry points) */
passthru: /* ARB_shader_bit_encoding (no entry points) */
passthru: /* ARB_texture_rgb10_a2ui (no entry points) */
passthru: /* ARB_texture_swizzle (no entry points) */
passthru: /* ARB_timer_query */
passthru: /* ARB_vertex_type_2_10_10_10_rev */


###############################################################################
###############################################################################
#
# OpenGL 4.0 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 4.0

# OpenGL 4.0 (ARB_sample_shading) commands

MinSampleShading(value)
	return		void
	param		value		ColorF in value
	category	VERSION_4_0
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# OpenGL 4.0 (ARB_draw_buffers_blend) commands

BlendEquationi(buf, mode)
	return		void
	param		buf		UInt32 in value
	param		mode		GLenum in value
	category	VERSION_4_0
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendEquationSeparatei(buf, modeRGB, modeAlpha)
	return		void
	param		buf		UInt32 in value
	param		modeRGB		GLenum in value
	param		modeAlpha	GLenum in value
	category	VERSION_4_0
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendFunci(buf, src, dst)
	return		void
	param		buf		UInt32 in value
	param		src		GLenum in value
	param		dst		GLenum in value
	category	VERSION_4_0
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendFuncSeparatei(buf, srcRGB, dstRGB, srcAlpha, dstAlpha)
	return		void
	param		buf		UInt32 in value
	param		srcRGB		GLenum in value
	param		dstRGB		GLenum in value
	param		srcAlpha	GLenum in value
	param		dstAlpha	GLenum in value
	category	VERSION_4_0
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

passthru: /* OpenGL 4.0 also reuses entry points from these extensions: */
passthru: /* ARB_texture_query_lod (no entry points) */
passthru: /* ARB_draw_indirect */
passthru: /* ARB_gpu_shader5 (no entry points) */
passthru: /* ARB_gpu_shader_fp64 */
passthru: /* ARB_shader_subroutine */
passthru: /* ARB_tessellation_shader */
passthru: /* ARB_texture_buffer_object_rgb32 (no entry points) */
passthru: /* ARB_texture_cube_map_array (no entry points) */
passthru: /* ARB_texture_gather (no entry points) */
passthru: /* ARB_transform_feedback2 */
passthru: /* ARB_transform_feedback3 */


###############################################################################
###############################################################################
#
# OpenGL 4.1 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 4.1 - none
newcategory: VERSION_4_1

passthru: /* OpenGL 4.1 reuses entry points from these extensions: */
passthru: /* ARB_ES2_compatibility */
passthru: /* ARB_get_program_binary */
passthru: /* ARB_separate_shader_objects */
passthru: /* ARB_shader_precision (no entry points) */
passthru: /* ARB_vertex_attrib_64bit */
passthru: /* ARB_viewport_array */


###############################################################################
###############################################################################
#
# OpenGL 4.2 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 4.2 - none
newcategory: VERSION_4_2

passthru: /* OpenGL 4.2 reuses entry points from these extensions: */
passthru: /* ARB_base_instance */
passthru: /* ARB_shading_language_420pack (no entry points) */
passthru: /* ARB_transform_feedback_instanced */
passthru: /* ARB_compressed_texture_pixel_storage (no entry points) */
passthru: /* ARB_conservative_depth (no entry points) */
passthru: /* ARB_internalformat_query */
passthru: /* ARB_map_buffer_alignment (no entry points) */
passthru: /* ARB_shader_atomic_counters */
passthru: /* ARB_shader_image_load_store */
passthru: /* ARB_shading_language_packing (no entry points) */
passthru: /* ARB_texture_storage */


###############################################################################
###############################################################################
#
# OpenGL 4.3 commands
#
###############################################################################
###############################################################################

# New commands in OpenGL 4.3 - none
newcategory: VERSION_4_3

passthru: /* OpenGL 4.3 reuses entry points from these extensions: */
passthru: /* ARB_arrays_of_arrays (no entry points, GLSL only) */
passthru: /* ARB_fragment_layer_viewport (no entry points, GLSL only) */
passthru: /* ARB_shader_image_size (no entry points, GLSL only) */
passthru: /* ARB_ES3_compatibility (no entry points) */
passthru: /* ARB_clear_buffer_object */
passthru: /* ARB_compute_shader */
passthru: /* ARB_copy_image */
passthru: /* KHR_debug (includes ARB_debug_output commands promoted to KHR without suffixes) */
passthru: /* ARB_explicit_uniform_location (no entry points) */
passthru: /* ARB_framebuffer_no_attachments */
passthru: /* ARB_internalformat_query2 */
passthru: /* ARB_invalidate_subdata */
passthru: /* ARB_multi_draw_indirect */
passthru: /* ARB_program_interface_query */
passthru: /* ARB_robust_buffer_access_behavior (no entry points) */
passthru: /* ARB_shader_storage_buffer_object */
passthru: /* ARB_stencil_texturing (no entry points) */
passthru: /* ARB_texture_buffer_range */
passthru: /* ARB_texture_query_levels (no entry points) */
passthru: /* ARB_texture_storage_multisample */
passthru: /* ARB_texture_view */
passthru: /* ARB_vertex_attrib_binding */

###############################################################################
###############################################################################
#
# ARB extensions, in order by ARB extension number
#
###############################################################################
###############################################################################

###############################################################################
#
# ARB Extension #1
# ARB_multitexture commands
#
###############################################################################

ActiveTextureARB(texture)
	return		void
	param		texture		TextureUnit in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	197
	alias		ActiveTexture

ClientActiveTextureARB(texture)
	return		void
	param		texture		TextureUnit in value
	category	ARB_multitexture
	dlflags		notlistable
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.2
	alias		ClientActiveTexture

MultiTexCoord1dARB(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord1dv

MultiTexCoord1dvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [1]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	198
	alias		MultiTexCoord1dv

MultiTexCoord1fARB(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord1fv

MultiTexCoord1fvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [1]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	199
	alias		MultiTexCoord1fv

MultiTexCoord1iARB(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord1iv

MultiTexCoord1ivARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [1]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	200
	alias		MultiTexCoord1iv

MultiTexCoord1sARB(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord1sv

MultiTexCoord1svARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [1]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	201
	alias		MultiTexCoord1sv

MultiTexCoord2dARB(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	param		t		CoordD in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord2dv

MultiTexCoord2dvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [2]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	202
	alias		MultiTexCoord2dv

MultiTexCoord2fARB(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	param		t		CoordF in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord2fv

MultiTexCoord2fvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [2]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	203
	alias		MultiTexCoord2fv

MultiTexCoord2iARB(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	param		t		CoordI in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord2iv

MultiTexCoord2ivARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [2]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	204
	alias		MultiTexCoord2iv

MultiTexCoord2sARB(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	param		t		CoordS in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord2sv

MultiTexCoord2svARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [2]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	205
	alias		MultiTexCoord2sv

MultiTexCoord3dARB(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	param		t		CoordD in value
	param		r		CoordD in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord3dv

MultiTexCoord3dvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [3]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	206
	alias		MultiTexCoord3dv

MultiTexCoord3fARB(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	param		t		CoordF in value
	param		r		CoordF in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord3fv

MultiTexCoord3fvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [3]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	207
	alias		MultiTexCoord3fv

MultiTexCoord3iARB(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	param		t		CoordI in value
	param		r		CoordI in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord3iv

MultiTexCoord3ivARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [3]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	208
	alias		MultiTexCoord3iv

MultiTexCoord3sARB(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	param		t		CoordS in value
	param		r		CoordS in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord3sv

MultiTexCoord3svARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [3]
	category	ARB_multitexture
	version		1.2
	glxflags	ARB
	glxropcode	209
	alias		MultiTexCoord3sv

MultiTexCoord4dARB(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordD in value
	param		t		CoordD in value
	param		r		CoordD in value
	param		q		CoordD in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord4dv

MultiTexCoord4dvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordD in array [4]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	210
	alias		MultiTexCoord4dv

MultiTexCoord4fARB(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordF in value
	param		t		CoordF in value
	param		r		CoordF in value
	param		q		CoordF in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord4fv

MultiTexCoord4fvARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordF in array [4]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	211
	alias		MultiTexCoord4fv

MultiTexCoord4iARB(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordI in value
	param		t		CoordI in value
	param		r		CoordI in value
	param		q		CoordI in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord4iv

MultiTexCoord4ivARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordI in array [4]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	212
	alias		MultiTexCoord4iv

MultiTexCoord4sARB(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		CoordS in value
	param		t		CoordS in value
	param		r		CoordS in value
	param		q		CoordS in value
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	vectorequiv	MultiTexCoord4sv

MultiTexCoord4svARB(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		CoordS in array [4]
	category	ARB_multitexture
	glxflags	ARB
	version		1.2
	glxropcode	213
	alias		MultiTexCoord4sv

################################################################################
#
# ARB Extension #2 - GLX_ARB_get_proc_address
#
###############################################################################

################################################################################
#
# ARB Extension #3
# ARB_transpose_matrix commands
#
###############################################################################

LoadTransposeMatrixfARB(m)
	return		void
	param		m		Float32 in array [16]
	category	ARB_transpose_matrix
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.2
	alias		LoadTransposeMatrixf

LoadTransposeMatrixdARB(m)
	return		void
	param		m		Float64 in array [16]
	category	ARB_transpose_matrix
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.2
	alias		LoadTransposeMatrixd

MultTransposeMatrixfARB(m)
	return		void
	param		m		Float32 in array [16]
	category	ARB_transpose_matrix
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.2
	alias		MultTransposeMatrixf

MultTransposeMatrixdARB(m)
	return		void
	param		m		Float64 in array [16]
	category	ARB_transpose_matrix
	glxflags	ARB client-handcode client-intercept server-handcode
	version		1.2
	alias		MultTransposeMatrixd

################################################################################
#
# ARB Extension #4 - WGL_ARB_buffer_region
#
###############################################################################

################################################################################
#
# ARB Extension #5
# ARB_multisample commands
#
###############################################################################

SampleCoverageARB(value, invert)
	return		void
	param		value		Float32 in value
	param		invert		Boolean in value
	category	ARB_multisample
	glxflags	ARB
	version		1.2
	alias		SampleCoverage

################################################################################
#
# ARB Extension #6
# ARB_texture_env_add commands
#
###############################################################################

# (none)
newcategory: ARB_texture_env_add

################################################################################
#
# ARB Extension #7
# ARB_texture_cube_map commands
#
###############################################################################

# (none)
newcategory: ARB_texture_cube_map

################################################################################
#
# ARB Extension #8 - WGL_ARB_extensions_string
# ARB Extension #9 - WGL_ARB_pixel_format commands
# ARB Extension #10 - WGL_ARB_make_current_read commands
# ARB Extension #11 - WGL_ARB_pbuffer
#
###############################################################################

################################################################################
#
# ARB Extension #12
# ARB_texture_compression commands
#
###############################################################################

# Arguably TexelInternalFormat, not PixelInternalFormat
CompressedTexImage3DARB(target, level, internalformat, width, height, depth, border, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	ARB_texture_compression
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxropcode	216
	alias		CompressedTexImage3D
	wglflags	client-handcode server-handcode

# Arguably TexelInternalFormat, not PixelInternalFormat
CompressedTexImage2DARB(target, level, internalformat, width, height, border, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	ARB_texture_compression
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxropcode	215
	alias		CompressedTexImage2D
	wglflags	client-handcode server-handcode

# Arguably TexelInternalFormat, not PixelInternalFormat
CompressedTexImage1DARB(target, level, internalformat, width, border, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	ARB_texture_compression
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxropcode	214
	alias		CompressedTexImage1D
	wglflags	client-handcode server-handcode

CompressedTexSubImage3DARB(target, level, xoffset, yoffset, zoffset, width, height, depth, format, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	ARB_texture_compression
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxropcode	219
	alias		CompressedTexSubImage3D
	wglflags	client-handcode server-handcode

CompressedTexSubImage2DARB(target, level, xoffset, yoffset, width, height, format, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	ARB_texture_compression
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxropcode	218
	alias		CompressedTexSubImage2D
	wglflags	client-handcode server-handcode

CompressedTexSubImage1DARB(target, level, xoffset, width, format, imageSize, data)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		data		CompressedTextureARB in array [imageSize]
	category	ARB_texture_compression
	dlflags		handcode
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxropcode	217
	alias		CompressedTexSubImage1D
	wglflags	client-handcode server-handcode

GetCompressedTexImageARB(target, level, img)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		img		CompressedTextureARB out array [COMPSIZE(target/level)]
	category	ARB_texture_compression
	dlflags		notlistable
	glxflags	ARB client-handcode server-handcode
	version		1.2
	glxsingle	160
	alias		GetCompressedTexImage
	wglflags	client-handcode server-handcode

################################################################################
#
# ARB Extension #13
# ARB_texture_border_clamp commands
#
###############################################################################

# (none)
newcategory: ARB_texture_border_clamp

###############################################################################
#
# ARB Extension #14
# ARB_point_parameters commands
#
###############################################################################

PointParameterfARB(pname, param)
	return		void
	param		pname		PointParameterNameARB in value
	param		param		CheckedFloat32 in value
	category	ARB_point_parameters
	version		1.0
	glxflags	ARB
	glxropcode	2065
	extension
	alias		PointParameterf

PointParameterfvARB(pname, params)
	return		void
	param		pname		PointParameterNameARB in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	ARB_point_parameters
	version		1.0
	glxflags	ARB
	glxropcode	2066
	extension
	alias		PointParameterfv

################################################################################
#
# ARB Extension #15
# ARB_vertex_blend commands
#
###############################################################################

WeightbvARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		Int8 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	220
	glxflags	ignore
	offset		?

WeightsvARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		Int16 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	222
	glxflags	ignore
	offset		?

WeightivARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		Int32 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	224
	glxflags	ignore
	offset		?

WeightfvARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		Float32 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	227
	glxflags	ignore
	offset		?

WeightdvARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		Float64 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	228
	glxflags	ignore
	offset		?

WeightubvARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		UInt8 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	221
	glxflags	ignore
	offset		?

WeightusvARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		UInt16 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	223
	glxflags	ignore
	offset		?

WeightuivARB(size, weights)
	return		void
	param		size		Int32 in value
	param		weights		UInt32 in array [size]
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	225
	glxflags	ignore
	offset		?

WeightPointerARB(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		WeightPointerTypeARB in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	ARB_vertex_blend
	version		1.1
	extension
	dlflags		notlistable
	glxflags	ignore
	offset		?

VertexBlendARB(count)
	return		void
	param		count		Int32 in value
	category	ARB_vertex_blend
	version		1.1
	extension
	glxropcode	226
	glxflags	ignore
	offset		?

################################################################################
#
# ARB Extension #16
# ARB_matrix_palette commands
#
###############################################################################

CurrentPaletteMatrixARB(index)
	return		void
	param		index		Int32 in value
	category	ARB_matrix_palette
	version		1.1
	extension
	glxropcode	4329
	glxflags	ignore
	offset		?

MatrixIndexubvARB(size, indices)
	return		void
	param		size		Int32 in value
	param		indices		UInt8 in array [size]
	category	ARB_matrix_palette
	version		1.1
	extension
	glxropcode	4326
	glxflags	ignore
	offset		?

MatrixIndexusvARB(size, indices)
	return		void
	param		size		Int32 in value
	param		indices		UInt16 in array [size]
	category	ARB_matrix_palette
	version		1.1
	extension
	glxropcode	4327
	glxflags	ignore
	offset		?

MatrixIndexuivARB(size, indices)
	return		void
	param		size		Int32 in value
	param		indices		UInt32 in array [size]
	category	ARB_matrix_palette
	version		1.1
	extension
	glxropcode	4328
	glxflags	ignore
	offset		?

MatrixIndexPointerARB(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		MatrixIndexPointerTypeARB in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	ARB_matrix_palette
	version		1.1
	extension
	dlflags		notlistable
	glxflags	ignore
	offset		?

################################################################################
#
# ARB Extension #17
# ARB_texture_env_combine commands
#
###############################################################################

# (none)
newcategory: ARB_texture_env_combine

################################################################################
#
# ARB Extension #18
# ARB_texture_env_crossbar commands
#
###############################################################################

# (none)
newcategory: ARB_texture_env_crossbar

################################################################################
#
# ARB Extension #19
# ARB_texture_env_dot3 commands
#
###############################################################################

# (none)
newcategory: ARB_texture_env_dot3

###############################################################################
#
# ARB Extension #20 - WGL_ARB_render_texture
#
###############################################################################

###############################################################################
#
# ARB Extension #21
# ARB_texture_mirrored_repeat commands
#
###############################################################################

# (none)
newcategory: ARB_texture_mirrored_repeat

###############################################################################
#
# ARB Extension #22
# ARB_depth_texture commands
#
###############################################################################

# (none)
newcategory: ARB_depth_texture

###############################################################################
#
# ARB Extension #23
# ARB_shadow commands
#
###############################################################################

# (none)
newcategory: ARB_shadow

###############################################################################
#
# ARB Extension #24
# ARB_shadow_ambient commands
#
###############################################################################

# (none)
newcategory: ARB_shadow_ambient

###############################################################################
#
# ARB Extension #25
# ARB_window_pos commands
# Note: all entry points use glxropcode ropcode 230, with 3 float parameters
#
###############################################################################

WindowPos2dARB(x, y)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	category	ARB_window_pos
	vectorequiv	WindowPos2dvARB
	version		1.0
	alias		WindowPos2d

WindowPos2dvARB(v)
	return		void
	param		v		CoordD in array [2]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos2dv

WindowPos2fARB(x, y)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	category	ARB_window_pos
	vectorequiv	WindowPos2fvARB
	version		1.0
	alias		WindowPos2f

WindowPos2fvARB(v)
	return		void
	param		v		CoordF in array [2]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos2fv

WindowPos2iARB(x, y)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	category	ARB_window_pos
	vectorequiv	WindowPos2ivARB
	version		1.0
	alias		WindowPos2i

WindowPos2ivARB(v)
	return		void
	param		v		CoordI in array [2]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos2iv

WindowPos2sARB(x, y)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	category	ARB_window_pos
	vectorequiv	WindowPos2svARB
	version		1.0
	alias		WindowPos2s

WindowPos2svARB(v)
	return		void
	param		v		CoordS in array [2]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos2sv

WindowPos3dARB(x, y, z)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	vectorequiv	WindowPos3dvARB
	category	ARB_window_pos
	version		1.0
	alias		WindowPos3d

WindowPos3dvARB(v)
	return		void
	param		v		CoordD in array [3]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos3dv

WindowPos3fARB(x, y, z)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	category	ARB_window_pos
	vectorequiv	WindowPos3fvARB
	version		1.0
	alias		WindowPos3f

WindowPos3fvARB(v)
	return		void
	param		v		CoordF in array [3]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos3fv

WindowPos3iARB(x, y, z)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	category	ARB_window_pos
	vectorequiv	WindowPos3ivARB
	version		1.0
	alias		WindowPos3i

WindowPos3ivARB(v)
	return		void
	param		v		CoordI in array [3]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos3iv

WindowPos3sARB(x, y, z)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	category	ARB_window_pos
	vectorequiv	WindowPos3svARB
	version		1.0
	alias		WindowPos3s

WindowPos3svARB(v)
	return		void
	param		v		CoordS in array [3]
	category	ARB_window_pos
	version		1.0
	glxropcode	230
	glxflags	client-handcode server-handcode
	alias		WindowPos3sv

###############################################################################
#
# ARB Extension #26
# ARB_vertex_program commands
#
###############################################################################

VertexAttrib1dARB(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib1dvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib1d

VertexAttrib1dvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [1]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4197
	alias		VertexAttrib1dv

VertexAttrib1fARB(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib1fvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib1f

VertexAttrib1fvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [1]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4193
	alias		VertexAttrib1fv

VertexAttrib1sARB(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib1svARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib1s

VertexAttrib1svARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [1]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4189
	alias		VertexAttrib1sv

VertexAttrib2dARB(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib2dvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib2d

VertexAttrib2dvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [2]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4198
	alias		VertexAttrib2dv

VertexAttrib2fARB(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib2fvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib2f

VertexAttrib2fvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [2]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4194
	alias		VertexAttrib2fv

VertexAttrib2sARB(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib2svARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib2s

VertexAttrib2svARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [2]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4190
	alias		VertexAttrib2sv

VertexAttrib3dARB(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib3dvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib3d

VertexAttrib3dvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [3]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4199
	alias		VertexAttrib3dv

VertexAttrib3fARB(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib3fvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib3f

VertexAttrib3fvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [3]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4195
	alias		VertexAttrib3fv

VertexAttrib3sARB(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib3svARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib3s

VertexAttrib3svARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [3]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4191
	alias		VertexAttrib3sv

VertexAttrib4NbvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int8 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4Nbv

VertexAttrib4NivARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4Niv

VertexAttrib4NsvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4Nsv

VertexAttrib4NubARB(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		UInt8 in value
	param		y		UInt8 in value
	param		z		UInt8 in value
	param		w		UInt8 in value
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4Nub

VertexAttrib4NubvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt8 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4201
	alias		VertexAttrib4Nubv

VertexAttrib4NuivARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4Nuiv

VertexAttrib4NusvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt16 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4Nusv

VertexAttrib4bvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int8 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4bv

VertexAttrib4dARB(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib4dvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib4d

VertexAttrib4dvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4200
	alias		VertexAttrib4dv

VertexAttrib4fARB(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib4fvARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib4f

VertexAttrib4fvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4196
	alias		VertexAttrib4fv

VertexAttrib4ivARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4iv

VertexAttrib4sARB(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	param		w		Int16 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	VertexAttrib4svARB
	extension	soft WINSOFT NV10
	alias		VertexAttrib4s

VertexAttrib4svARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4192
	alias		VertexAttrib4sv

VertexAttrib4ubvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt8 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4ubv

VertexAttrib4uivARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4uiv

VertexAttrib4usvARB(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt16 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttrib4usv

VertexAttribPointerARB(index, size, type, normalized, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		VertexAttribPointerTypeARB in value
	param		normalized	Boolean in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		VertexAttribPointer

EnableVertexAttribArrayARB(index)
	return		void
	param		index		UInt32 in value
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		EnableVertexAttribArray

DisableVertexAttribArrayARB(index)
	return		void
	param		index		UInt32 in value
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	alias		DisableVertexAttribArray

ProgramStringARB(target, format, len, string)
	return		void
	param		target		ProgramTargetARB in value
	param		format		ProgramFormatARB in value
	param		len		SizeI in value
	param		string		Void in array [len]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		667

BindProgramARB(target, program)
	return		void
	param		target		ProgramTargetARB in value
	param		program		UInt32 in value
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxropcode	4180
	offset		579

DeleteProgramsARB(n, programs)
	return		void
	param		n		SizeI in value
	param		programs	UInt32 in array [n]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxvendorpriv	1294
	offset		580

GenProgramsARB(n, programs)
	return		void
	param		n		SizeI in value
	param		programs	UInt32 out array [n]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxvendorpriv	1295
	offset		582

ProgramEnvParameter4dARB(target, index, x, y, z, w)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	ProgramEnvParameter4dvARB
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		668

ProgramEnvParameter4dvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float64 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		669

ProgramEnvParameter4fARB(target, index, x, y, z, w)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	ProgramEnvParameter4fvARB
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		670

ProgramEnvParameter4fvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		671

ProgramLocalParameter4dARB(target, index, x, y, z, w)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	ProgramLocalParameter4dvARB
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		672

ProgramLocalParameter4dvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float64 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		673

ProgramLocalParameter4fARB(target, index, x, y, z, w)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	ARB_vertex_program
	version		1.3
	vectorequiv	ProgramLocalParameter4fvARB
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		674

ProgramLocalParameter4fvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float32 in array [4]
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		675

GetProgramEnvParameterdvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float64 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		676

GetProgramEnvParameterfvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float32 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		677

GetProgramLocalParameterdvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float64 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		678

GetProgramLocalParameterfvARB(target, index, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		params		Float32 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		679

GetProgramivARB(target, pname, params)
	return		void
	param		target		ProgramTargetARB in value
	param		pname		ProgramPropertyARB in value
	param		params		Int32 out array [1]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		680

GetProgramStringARB(target, pname, string)
	return		void
	param		target		ProgramTargetARB in value
	param		pname		ProgramStringPropertyARB in value
	param		string		Void out array [COMPSIZE(target,pname)]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		681

GetVertexAttribdvARB(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPropertyARB in value
	param		params		Float64 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxvendorpriv	1301
	alias		GetVertexAttribdv

GetVertexAttribfvARB(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPropertyARB in value
	param		params		Float32 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxvendorpriv	1302
	alias		GetVertexAttribfv

GetVertexAttribivARB(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPropertyARB in value
	param		params		Int32 out array [4]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxvendorpriv	1303
	alias		GetVertexAttribiv

GetVertexAttribPointervARB(index, pname, pointer)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribPointerPropertyARB in value
	param		pointer		VoidPointer out array [1]
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxflags	ignore
	alias		GetVertexAttribPointerv

IsProgramARB(program)
	return		Boolean
	param		program		UInt32 in value
	dlflags		notlistable
	category	ARB_vertex_program
	version		1.3
	extension	soft WINSOFT NV10
	glxvendorpriv	1304
	alias		IsProgram


###############################################################################
#
# ARB Extension #27
# ARB_fragment_program commands
#
###############################################################################

# All ARB_fragment_program entry points are shared with ARB_vertex_program,
#   and are only included in that #define block, for now.
newcategory: ARB_fragment_program
passthru: /* All ARB_fragment_program entry points are shared with ARB_vertex_program. */

###############################################################################
#
# ARB Extension #28
# ARB_vertex_buffer_object commands
#
###############################################################################

BindBufferARB(target, buffer)
	return		void
	param		target		BufferTargetARB in value
	param		buffer		UInt32 in value
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		BindBuffer

DeleteBuffersARB(n, buffers)
	return		void
	param		n		SizeI in value
	param		buffers		ConstUInt32 in array [n]
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		DeleteBuffers

GenBuffersARB(n, buffers)
	return		void
	param		n		SizeI in value
	param		buffers		UInt32 out array [n]
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		GenBuffers

IsBufferARB(buffer)
	return		Boolean
	param		buffer		UInt32 in value
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		IsBuffer

BufferDataARB(target, size, data, usage)
	return		void
	param		target		BufferTargetARB in value
	param		size		BufferSizeARB in value
	param		data		ConstVoid in array [size]
	param		usage		BufferUsageARB in value
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		BufferData

BufferSubDataARB(target, offset, size, data)
	return		void
	param		target		BufferTargetARB in value
	param		offset		BufferOffsetARB in value
	param		size		BufferSizeARB in value
	param		data		ConstVoid in array [size]
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		BufferSubData

GetBufferSubDataARB(target, offset, size, data)
	return		void
	param		target		BufferTargetARB in value
	param		offset		BufferOffsetARB in value
	param		size		BufferSizeARB in value
	param		data		Void out array [size]
	category	ARB_vertex_buffer_object
	dlflags		notlistable
	version		1.2
	extension
	alias		GetBufferSubData

MapBufferARB(target, access)
	return		VoidPointer
	param		target		BufferTargetARB in value
	param		access		BufferAccessARB in value
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		MapBuffer

UnmapBufferARB(target)
	return		Boolean
	param		target		BufferTargetARB in value
	category	ARB_vertex_buffer_object
	version		1.2
	extension
	alias		UnmapBuffer

GetBufferParameterivARB(target, pname, params)
	return		void
	param		target		BufferTargetARB in value
	param		pname		BufferPNameARB in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_vertex_buffer_object
	dlflags		notlistable
	version		1.2
	extension
	alias		GetBufferParameteriv

GetBufferPointervARB(target, pname, params)
	return		void
	param		target		BufferTargetARB in value
	param		pname		BufferPointerNameARB in value
	param		params		VoidPointer out array [1]
	category	ARB_vertex_buffer_object
	dlflags		notlistable
	version		1.2
	extension
	alias		GetBufferPointerv

###############################################################################
#
# ARB Extension #29
# ARB_occlusion_query commands
#
###############################################################################

GenQueriesARB(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 out array [n]
	category	ARB_occlusion_query
	version		1.5
	extension
	alias		GenQueries

DeleteQueriesARB(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 in array [n]
	category	ARB_occlusion_query
	version		1.5
	extension
	alias		DeleteQueries

IsQueryARB(id)
	return		Boolean
	param		id		UInt32 in value
	category	ARB_occlusion_query
	version		1.5
	extension
	alias		IsQuery

BeginQueryARB(target, id)
	return		void
	param		target		GLenum in value
	param		id		UInt32 in value
	category	ARB_occlusion_query
	version		1.5
	extension
	alias		BeginQuery

EndQueryARB(target)
	return		void
	param		target		GLenum in value
	category	ARB_occlusion_query
	version		1.5
	extension
	alias		EndQuery

GetQueryivARB(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	ARB_occlusion_query
	dlflags		notlistable
	version		1.5
	extension
	alias		GetQueryiv

GetQueryObjectivARB(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	ARB_occlusion_query
	dlflags		notlistable
	version		1.5
	extension
	alias		GetQueryObjectiv

GetQueryObjectuivARB(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt32 out array [pname]
	category	ARB_occlusion_query
	dlflags		notlistable
	version		1.5
	extension
	alias		GetQueryObjectuiv

###############################################################################
#
# ARB Extension #30
# ARB_shader_objects commands
#
###############################################################################

DeleteObjectARB(obj)
	return		void
	param		obj		handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetHandleARB(pname)
	return		handleARB
	param		pname		GLenum in value
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

DetachObjectARB(containerObj, attachedObj)
	return		void
	param		containerObj	handleARB in value
	param		attachedObj	handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		DetachShader

CreateShaderObjectARB(shaderType)
	return		handleARB
	param		shaderType	GLenum in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		CreateShader

ShaderSourceARB(shaderObj, count, string, length)
	return		void
	param		shaderObj	handleARB in value
	param		count		SizeI in value
	param		string		charPointerARB in array [count]
	param		length		Int32 in array [1]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		ShaderSource

CompileShaderARB(shaderObj)
	return		void
	param		shaderObj	handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		CompileShader

CreateProgramObjectARB()
	return		handleARB
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		CreateProgram

AttachObjectARB(containerObj, obj)
	return		void
	param		containerObj	handleARB in value
	param		obj		handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		AttachShader

LinkProgramARB(programObj)
	return		void
	param		programObj	handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		LinkProgram

UseProgramObjectARB(programObj)
	return		void
	param		programObj	handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		UseProgram

ValidateProgramARB(programObj)
	return		void
	param		programObj	handleARB in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		ValidateProgram

Uniform1fARB(location, v0)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform1f

Uniform2fARB(location, v0, v1)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform2f

Uniform3fARB(location, v0, v1, v2)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform3f

Uniform4fARB(location, v0, v1, v2, v3)
	return		void
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	param		v3		Float32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform4f

Uniform1iARB(location, v0)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform1i

Uniform2iARB(location, v0, v1)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform2i

Uniform3iARB(location, v0, v1, v2)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform3i

Uniform4iARB(location, v0, v1, v2, v3)
	return		void
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	param		v3		Int32 in value
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform4i

Uniform1fvARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform1fv

Uniform2fvARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform2fv

Uniform3fvARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform3fv

Uniform4fvARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform4fv

Uniform1ivARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform1iv

Uniform2ivARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform2iv

Uniform3ivARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform3iv

Uniform4ivARB(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		Uniform4iv

UniformMatrix2fvARB(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		UniformMatrix2fv

UniformMatrix3fvARB(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		UniformMatrix3fv

UniformMatrix4fvARB(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		UniformMatrix4fv

GetObjectParameterfvARB(obj, pname, params)
	return		void
	param		obj		handleARB in value
	param		pname		GLenum in value
	param		params		Float32 out array [pname]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetObjectParameterivARB(obj, pname, params)
	return		void
	param		obj		handleARB in value
	param		pname		GLenum in value
	param		params		Int32 out array [pname]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetInfoLogARB(obj, maxLength, length, infoLog)
	return		void
	param		obj		handleARB in value
	param		maxLength	SizeI in value
	param		length		SizeI out array [1]
	param		infoLog		charARB out array [length]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetAttachedObjectsARB(containerObj, maxCount, count, obj)
	return		void
	param		containerObj	handleARB in value
	param		maxCount	SizeI in value
	param		count		SizeI out array [1]
	param		obj		handleARB out array [count]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetAttachedShaders

GetUniformLocationARB(programObj, name)
	return		Int32
	param		programObj	handleARB in value
	param		name		charARB in array []
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetUniformLocation

GetActiveUniformARB(programObj, index, maxLength, length, size, type, name)
	return		void
	param		programObj	handleARB in value
	param		index		UInt32 in value
	param		maxLength	SizeI in value
	param		length		SizeI out array [1]
	param		size		Int32 out array [1]
	param		type		GLenum out array [1]
	param		name		charARB out array []
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetActiveUniform

GetUniformfvARB(programObj, location, params)
	return		void
	param		programObj	handleARB in value
	param		location	Int32 in value
	param		params		Float32 out array [COMPSIZE(location)]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetUniformfv

GetUniformivARB(programObj, location, params)
	return		void
	param		programObj	handleARB in value
	param		location	Int32 in value
	param		params		Int32 out array [COMPSIZE(location)]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetUniformiv

GetShaderSourceARB(obj, maxLength, length, source)
	return		void
	param		obj		handleARB in value
	param		maxLength	SizeI in value
	param		length		SizeI out array [1]
	param		source		charARB out array [length]
	category	ARB_shader_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetShaderSource


###############################################################################
#
# ARB Extension #31
# ARB_vertex_shader commands
#
###############################################################################

BindAttribLocationARB(programObj, index, name)
	return		void
	param		programObj	handleARB in value
	param		index		UInt32 in value
	param		name		charARB in array []
	category	ARB_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		BindAttribLocation

GetActiveAttribARB(programObj, index, maxLength, length, size, type, name)
	return		void
	param		programObj	handleARB in value
	param		index		UInt32 in value
	param		maxLength	SizeI in value
	param		length		SizeI out array [1]
	param		size		Int32 out array [1]
	param		type		GLenum out array [1]
	param		name		charARB out array []
	category	ARB_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetActiveAttrib

GetAttribLocationARB(programObj, name)
	return		Int32
	param		programObj	handleARB in value
	param		name		charARB in array []
	category	ARB_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	alias		GetAttribLocation

###############################################################################
#
# ARB Extension #32
# ARB_fragment_shader commands
#
###############################################################################

#  (none)
newcategory: ARB_fragment_shader

###############################################################################
#
# ARB Extension #33
# ARB_shading_language_100 commands
#
###############################################################################

#  (none)
newcategory: ARB_shading_language_100

###############################################################################
#
# ARB Extension #34
# ARB_texture_non_power_of_two commands
#
###############################################################################

# (none)
newcategory: ARB_texture_non_power_of_two

###############################################################################
#
# ARB Extension #35
# ARB_point_sprite commands
#
###############################################################################

# (none)
newcategory: ARB_point_sprite

###############################################################################
#
# ARB Extension #36
# ARB_fragment_program_shadow commands
#
###############################################################################

# (none)
newcategory: ARB_fragment_program_shadow

###############################################################################
#
# ARB Extension #37
# ARB_draw_buffers commands
#
###############################################################################

DrawBuffersARB(n, bufs)
	return		void
	param		n		SizeI in value
	param		bufs		DrawBufferModeATI in array [n]
	category	ARB_draw_buffers
	version		1.5
	extension
	alias		DrawBuffers

###############################################################################
#
# ARB Extension #38
# ARB_texture_rectangle commands
#
###############################################################################

# (none)
newcategory: ARB_texture_rectangle

###############################################################################
#
# ARB Extension #39
# ARB_color_buffer_float commands
#
###############################################################################

ClampColorARB(target, clamp)
	return		void
	param		target		ClampColorTargetARB in value
	param		clamp		ClampColorModeARB in value
	category	ARB_color_buffer_float
	version		1.5
	extension
	glxropcode	234
	glxflags	ignore
	alias		ClampColor

###############################################################################
#
# ARB Extension #40
# ARB_half_float_pixel commands
#
###############################################################################

# (none)
newcategory: ARB_half_float_pixel

###############################################################################
#
# ARB Extension #41
# ARB_texture_float commands
#
###############################################################################

# (none)
newcategory: ARB_texture_float

###############################################################################
#
# ARB Extension #42
# ARB_pixel_buffer_object commands
#
###############################################################################

# (none)
newcategory: ARB_pixel_buffer_object

###############################################################################
#
# ARB Extension #43
# ARB_depth_buffer_float commands (also OpenGL 3.0)
#
###############################################################################

# (none)
newcategory: ARB_depth_buffer_float

###############################################################################
#
# ARB Extension #44
# ARB_draw_instanced commands
#
###############################################################################

DrawArraysInstancedARB(mode, first, count, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in value
	param		count		SizeI in value
	param		primcount	SizeI in value
	category	ARB_draw_instanced
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	vectorequiv	ArrayElement
	glfflags	ignore
	glxflags	ignore
	alias		DrawArraysInstanced

DrawElementsInstancedARB(mode, count, type, indices, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	param		primcount	SizeI in value
	category	ARB_draw_instanced
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	vectorequiv	ArrayElement
	glfflags	ignore
	glxflags	ignore
	alias		DrawElementsInstanced

###############################################################################
#
# ARB Extension #45
# ARB_framebuffer_object commands (also OpenGL 3.0)
#
###############################################################################

# Promoted from EXT_framebuffer_object
IsRenderbuffer(renderbuffer)
	return		Boolean
	param		renderbuffer	UInt32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxvendorpriv	1422
	glxflags	ignore
	offset		?

# GLX opcode changed so it can be differentiated from BindRenderbufferEXT
# (see ARB_framebuffer_object extension spec revision 23)
BindRenderbuffer(target, renderbuffer)
	return		void
	param		target		RenderbufferTarget in value
	param		renderbuffer	UInt32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	235
	glxflags	ignore
	offset		?

DeleteRenderbuffers(n, renderbuffers)
	return		void
	param		n		SizeI in value
	param		renderbuffers	UInt32 in array [n]
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4317
	glxflags	ignore
	offset		?

GenRenderbuffers(n, renderbuffers)
	return		void
	param		n		SizeI in value
	param		renderbuffers	UInt32 out array [n]
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxvendorpriv	1423
	glxflags	ignore
	offset		?

RenderbufferStorage(target, internalformat, width, height)
	return		void
	param		target		RenderbufferTarget in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4318
	glxflags	ignore
	offset		?

GetRenderbufferParameteriv(target, pname, params)
	return		void
	param		target		RenderbufferTarget in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_framebuffer_object
	dlflags		notlistable
	version		3.0
	extension
	glxvendorpriv	1424
	glxflags	ignore
	offset		?

IsFramebuffer(framebuffer)
	return		Boolean
	param		framebuffer	UInt32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxvendorpriv	1425
	glxflags	ignore
	offset		?

# GLX opcode changed so it can be differentiated from BindFramebufferEXT
# (see ARB_framebuffer_object extension spec revision 23)
BindFramebuffer(target, framebuffer)
	return		void
	param		target		FramebufferTarget in value
	param		framebuffer	UInt32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	236
	glxflags	ignore
	offset		?

DeleteFramebuffers(n, framebuffers)
	return		void
	param		n		SizeI in value
	param		framebuffers	UInt32 in array [n]
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4320
	glxflags	ignore
	offset		?

GenFramebuffers(n, framebuffers)
	return		void
	param		n		SizeI in value
	param		framebuffers	UInt32 out array [n]
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxvendorpriv	1426
	glxflags	ignore
	offset		?

CheckFramebufferStatus(target)
	return		GLenum
	param		target		FramebufferTarget in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxvendorpriv	1427
	glxflags	ignore
	offset		?

FramebufferTexture1D(target, attachment, textarget, texture, level)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		textarget	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4321
	glxflags	ignore
	offset		?

FramebufferTexture2D(target, attachment, textarget, texture, level)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		textarget	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4322
	glxflags	ignore
	offset		?

FramebufferTexture3D(target, attachment, textarget, texture, level, zoffset)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		textarget	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		zoffset		Int32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4323
	glxflags	ignore
	offset		?

FramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		renderbuffertarget	RenderbufferTarget in value
	param		renderbuffer	UInt32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4324
	glxflags	ignore
	offset		?

GetFramebufferAttachmentParameteriv(target, attachment, pname, params)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_framebuffer_object
	dlflags		notlistable
	version		3.0
	extension
	glxvendorpriv	1428
	glxflags	ignore
	offset		?

GenerateMipmap(target)
	return		void
	param		target		GLenum in value
	category	ARB_framebuffer_object
	version		3.0
	extension
	glxropcode	4325
	glxflags	ignore
	offset		?

# Promoted from EXT_framebuffer_blit
BlitFramebuffer(srcX0, srcY0, srcX1, srcY1, dstX0, dstY0, dstX1, dstY1, mask, filter)
	return		void
	param		srcX0		Int32 in value
	param		srcY0		Int32 in value
	param		srcX1		Int32 in value
	param		srcY1		Int32 in value
	param		dstX0		Int32 in value
	param		dstY0		Int32 in value
	param		dstX1		Int32 in value
	param		dstY1		Int32 in value
	param		mask		ClearBufferMask in value
	param		filter		GLenum in value
	category	ARB_framebuffer_object
	version		3.0
	glxropcode	4330
	offset		?

# Promoted from EXT_framebuffer_multisample
RenderbufferStorageMultisample(target, samples, internalformat, width, height)
	return		void
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	ARB_framebuffer_object
	version		3.0
	glxropcode	4331
	offset		?

# Promoted from ARB_geometry_shader4
FramebufferTextureLayer(target, attachment, texture, level, layer)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		layer		CheckedInt32 in value
	category	ARB_framebuffer_object
	version		3.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxropcode	237
	offset		?


###############################################################################
#
# ARB Extension #46
# ARB_framebuffer_sRGB commands (also OpenGL 3.0)
#
###############################################################################

# (none)
newcategory: ARB_framebuffer_sRGB

###############################################################################
#
# ARB Extension #47
# ARB_geometry_shader4 commands
#
###############################################################################

ProgramParameteriARB(program, pname, value)
	return		void
	param		program		UInt32 in value
	param		pname		ProgramParameterPName in value
	param		value		Int32 in value
	category	ARB_geometry_shader4
	version		3.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		ProgramParameteri

FramebufferTextureARB(target, attachment, texture, level)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	category	ARB_geometry_shader4
	version		3.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

FramebufferTextureLayerARB(target, attachment, texture, level, layer)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		layer		CheckedInt32 in value
	category	ARB_geometry_shader4
	version		3.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	alias		FramebufferTextureLayer

FramebufferTextureFaceARB(target, attachment, texture, level, face)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		face		TextureTarget in value
	category	ARB_geometry_shader4
	version		3.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# ARB Extension #48
# ARB_half_float_vertex commands (also OpenGL 3.0)
#
###############################################################################

# (none)
newcategory: ARB_half_float_vertex

###############################################################################
#
# ARB Extension #49
# ARB_instanced_arrays commands
#
###############################################################################

VertexAttribDivisorARB(index, divisor)
	return		void
	param		index		UInt32 in value
	param		divisor		UInt32 in value
	category	ARB_instanced_arrays
	version		2.0
	extension
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# ARB Extension #50
# ARB_map_buffer_range commands (also OpenGL 3.0)
#
###############################################################################

MapBufferRange(target, offset, length, access)
	return		VoidPointer
	param		target		BufferTargetARB in value
	param		offset		BufferOffset in value
	param		length		BufferSize in value
	param		access		BufferAccessMask in value
	category	ARB_map_buffer_range
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# Promoted from APPLE_flush_buffer_range
FlushMappedBufferRange(target, offset, length)
	return		void
	param		target		BufferTargetARB in value
	param		offset		BufferOffset in value
	param		length		BufferSize in value
	category	ARB_map_buffer_range
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #51
# ARB_texture_buffer_object commands
#
###############################################################################

TexBufferARB(target, internalformat, buffer)
	return		void
	param		target		TextureTarget in value
	param		internalformat	GLenum in value
	param		buffer		UInt32 in value
	category	ARB_texture_buffer_object
	version		3.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	alias		TexBuffer

###############################################################################
#
# ARB Extension #52
# ARB_texture_compression_rgtc commands (also OpenGL 3.0)
#
###############################################################################

# (none)
newcategory: ARB_texture_compression_rgtc

###############################################################################
#
# ARB Extension #53
# ARB_texture_rg commands (also OpenGL 3.0)
#
###############################################################################

# (none)
newcategory: ARB_texture_rg

###############################################################################
#
# ARB Extension #54
# ARB_vertex_array_object commands (also OpenGL 3.0)
#
###############################################################################

# Promoted from APPLE_vertex_array_object
BindVertexArray(array)
	return		void
	param		array		UInt32 in value
	category	ARB_vertex_array_object
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteVertexArrays(n, arrays)
	return		void
	param		n		SizeI in value
	param		arrays		UInt32 in array [n]
	category	ARB_vertex_array_object
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GenVertexArrays(n, arrays)
	return		void
	param		n		SizeI in value
	param		arrays		UInt32 out array [n]
	category	ARB_vertex_array_object
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsVertexArray(array)
	return		Boolean
	param		array		UInt32 in value
	category	ARB_vertex_array_object
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #55 - WGL_ARB_create_context
# ARB Extension #56 - GLX_ARB_create_context
#
###############################################################################

###############################################################################
#
# ARB Extension #57
# ARB_uniform_buffer_object commands
#
###############################################################################

GetUniformIndices(program, uniformCount, uniformNames, uniformIndices)
	return		void
	param		program		UInt32 in value
	param		uniformCount	SizeI in value
	param		uniformNames	ConstCharPointer in array [COMPSIZE(uniformCount)]
	param		uniformIndices	UInt32 out array [COMPSIZE(uniformCount)]
	category	ARB_uniform_buffer_object
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveUniformsiv(program, uniformCount, uniformIndices, pname, params)
	return		void
	param		program		UInt32 in value
	param		uniformCount	SizeI in value
	param		uniformIndices	UInt32 in array [COMPSIZE(uniformCount)]
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_uniform_buffer_object
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveUniformName(program, uniformIndex, bufSize, length, uniformName)
	return		void
	param		program		UInt32 in value
	param		uniformIndex	UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		uniformName	Char out array [bufSize]
	category	ARB_uniform_buffer_object
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetUniformBlockIndex(program, uniformBlockName)
	return		UInt32
	param		program		UInt32 in value
	param		uniformBlockName	Char in array [COMPSIZE()]
	category	ARB_uniform_buffer_object
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveUniformBlockiv(program, uniformBlockIndex, pname, params)
	return		void
	param		program		UInt32 in value
	param		uniformBlockIndex	UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_uniform_buffer_object
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveUniformBlockName(program, uniformBlockIndex, bufSize, length, uniformBlockName)
	return		void
	param		program		UInt32 in value
	param		uniformBlockIndex	UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		uniformBlockName	Char out array [bufSize]
	category	ARB_uniform_buffer_object
	dlflags		notlistable
	version		2.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

UniformBlockBinding(program, uniformBlockIndex, uniformBlockBinding)
	return		void
	param		program		UInt32 in value
	param		uniformBlockIndex	UInt32 in value
	param		uniformBlockBinding	UInt32 in value
	category	ARB_uniform_buffer_object
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?


###############################################################################
#
# ARB Extension #58
# ARB_compatibility commands
#
###############################################################################

# (none)
newcategory: ARB_compatibility

###############################################################################
#
# ARB Extension #59
# ARB_copy_buffer commands
#
###############################################################################

CopyBufferSubData(readTarget, writeTarget, readOffset, writeOffset, size)
	return		void
	param		readTarget	GLenum in value
	param		writeTarget	GLenum in value
	param		readOffset	BufferOffset in value
	param		writeOffset	BufferOffset in value
	param		size		BufferSize in value
	category	ARB_copy_buffer
	version		3.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #60
# ARB_shader_texture_lod commands
#
###############################################################################

# (none)
newcategory: ARB_shader_texture_lod

###############################################################################
#
# ARB Extension #61
# ARB_depth_clamp commands
#
###############################################################################

# (none)
newcategory: ARB_depth_clamp

###############################################################################
#
# ARB Extension #62
# ARB_draw_elements_base_vertex commands
#
###############################################################################

DrawElementsBaseVertex(mode, count, type, indices, basevertex)
	return		void
	param		mode		GLenum in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	param		basevertex	Int32 in value
	category	ARB_draw_elements_base_vertex
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawRangeElementsBaseVertex(mode, start, end, count, type, indices, basevertex)
	return		void
	param		mode		GLenum in value
	param		start		UInt32 in value
	param		end		UInt32 in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	param		basevertex	Int32 in value
	category	ARB_draw_elements_base_vertex
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawElementsInstancedBaseVertex(mode, count, type, indices, instancecount, basevertex)
	return		void
	param		mode		GLenum in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	param		instancecount	SizeI in value
	param		basevertex	Int32 in value
	category	ARB_draw_elements_base_vertex
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiDrawElementsBaseVertex(mode, count, type, indices, drawcount, basevertex)
	return		void
	param		mode		GLenum in value
	param		count		SizeI in array [COMPSIZE(drawcount)]
	param		type		DrawElementsType in value
	param		indices		ConstVoidPointer in array [COMPSIZE(drawcount)]
	param		drawcount	SizeI in value
	param		basevertex	Int32 in array [COMPSIZE(drawcount)]
	category	ARB_draw_elements_base_vertex
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #63
# ARB_fragment_coord_conventions commands
#
###############################################################################

# (none)
newcategory: ARB_fragment_coord_conventions

###############################################################################
#
# ARB Extension #64
# ARB_provoking_vertex commands
#
###############################################################################

ProvokingVertex(mode)
	return		void
	param		mode		GLenum in value
	category	ARB_provoking_vertex
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #65
# ARB_seamless_cube_map commands
#
###############################################################################

# (none)
newcategory: ARB_seamless_cube_map

###############################################################################
#
# ARB Extension #66
# ARB_sync commands
#
###############################################################################

FenceSync(condition, flags)
	return		sync
	param		condition	GLenum in value
	param		flags		GLbitfield in value
	category	ARB_sync
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsSync(sync)
	return		Boolean
	param		sync		sync in value
	category	ARB_sync
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteSync(sync)
	return		void
	param		sync		sync in value
	category	ARB_sync
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClientWaitSync(sync, flags, timeout)
	return		GLenum
	param		sync		sync in value
	param		flags		GLbitfield in value
	param		timeout		UInt64 in value
	category	ARB_sync
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

WaitSync(sync, flags, timeout)
	return		void
	param		sync		sync in value
	param		flags		GLbitfield in value
	param		timeout		UInt64 in value
	category	ARB_sync
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetInteger64v(pname, params)
	return		void
	param		pname		GLenum in value
	param		params		Int64 out array [COMPSIZE(pname)]
	category	ARB_sync
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetSynciv(sync, pname, bufSize, length, values)
	return		void
	param		sync		sync in value
	param		pname		GLenum in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		values		Int32 out array [length]
	category	ARB_sync
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #67
# ARB_texture_multisample commands
#
###############################################################################

TexImage2DMultisample(target, samples, internalformat, width, height, fixedsamplelocations)
	return		void
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		fixedsamplelocations	Boolean in value
	category	ARB_texture_multisample
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexImage3DMultisample(target, samples, internalformat, width, height, depth, fixedsamplelocations)
	return		void
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		fixedsamplelocations	Boolean in value
	category	ARB_texture_multisample
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetMultisamplefv(pname, index, val)
	return		void
	param		pname		GLenum in value
	param		index		UInt32 in value
	param		val		Float32 out array [COMPSIZE(pname)]
	category	ARB_texture_multisample
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

SampleMaski(index, mask)
	return		void
	param		index		UInt32 in value
	param		mask		GLbitfield in value
	category	ARB_texture_multisample
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #68
# ARB_vertex_array_bgra commands
#
###############################################################################

# (none)
newcategory: ARB_vertex_array_bgra

###############################################################################
#
# ARB Extension #69
# ARB_draw_buffers_blend commands
#
###############################################################################

BlendEquationiARB(buf, mode)
	return		void
	param		buf		UInt32 in value
	param		mode		GLenum in value
	category	ARB_draw_buffers_blend
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?
	alias		BlendEquationi

BlendEquationSeparateiARB(buf, modeRGB, modeAlpha)
	return		void
	param		buf		UInt32 in value
	param		modeRGB		GLenum in value
	param		modeAlpha	GLenum in value
	category	ARB_draw_buffers_blend
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?
	alias		BlendEquationSeparatei

BlendFunciARB(buf, src, dst)
	return		void
	param		buf		UInt32 in value
	param		src		GLenum in value
	param		dst		GLenum in value
	category	ARB_draw_buffers_blend
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?
	alias		BlendFunci

BlendFuncSeparateiARB(buf, srcRGB, dstRGB, srcAlpha, dstAlpha)
	return		void
	param		buf		UInt32 in value
	param		srcRGB		GLenum in value
	param		dstRGB		GLenum in value
	param		srcAlpha	GLenum in value
	param		dstAlpha	GLenum in value
	category	ARB_draw_buffers_blend
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?
	alias		BlendFuncSeparatei

###############################################################################
#
# ARB Extension #70
# ARB_sample_shading commands
#
###############################################################################

MinSampleShadingARB(value)
	return		void
	param		value		ColorF in value
	category	ARB_sample_shading
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?
	alias		MinSampleShading

###############################################################################
#
# ARB Extension #71
# ARB_texture_cube_map_array commands
#
###############################################################################

# (none)
newcategory: ARB_texture_cube_map_array

###############################################################################
#
# ARB Extension #72
# ARB_texture_gather commands
#
###############################################################################

# (none)
newcategory: ARB_texture_gather

###############################################################################
#
# ARB Extension #73
# ARB_texture_query_lod commands
#
###############################################################################

# (none)
newcategory: ARB_texture_query_lod

###############################################################################
#
# ARB Extension #74 - WGL_ARB_create_context_profile
# ARB Extension #75 - GLX_ARB_create_context_profile
#
###############################################################################

###############################################################################
#
# ARB Extension #76
# ARB_shading_language_include commands
#
###############################################################################

NamedStringARB(type, namelen, name, stringlen, string)
	return		void
	param		type		GLenum in value
	param		namelen		Int32 in value
	param		name		Char in array [namelen]
	param		stringlen	Int32 in value
	param		string		Char in array [stringlen]
	category	ARB_shading_language_include
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteNamedStringARB(namelen, name)
	return		void
	param		namelen		Int32 in value
	param		name		Char in array [namelen]
	category	ARB_shading_language_include
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

CompileShaderIncludeARB(shader, count, path, length)
	return		void
	param		shader		UInt32 in value
	param		count		SizeI in value
	param		path		CharPointer in array [count]
	param		length		Int32 in array [count]
	category	ARB_shading_language_include
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsNamedStringARB(namelen, name)
	return		Boolean
	param		namelen		Int32 in value
	param		name		Char in array [namelen]
	category	ARB_shading_language_include
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetNamedStringARB(namelen, name, bufSize, stringlen, string)
	return		void
	param		namelen		Int32 in value
	param		name		Char in array [namelen]
	param		bufSize		SizeI in value
	param		stringlen	Int32 out array [1]
	param		string		Char out array [bufSize]
	category	ARB_shading_language_include
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetNamedStringivARB(namelen, name, pname, params)
	return		void
	param		namelen		Int32 in value
	param		name		Char in array [namelen]
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_shading_language_include
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #77
# ARB_texture_compression_bptc commands
#
###############################################################################

# (none)
newcategory: ARB_texture_compression_bptc

###############################################################################
#
# ARB Extension #78
# ARB_blend_func_extended commands
#
###############################################################################

BindFragDataLocationIndexed(program, colorNumber, index, name)
	return		void
	param		program		UInt32 in value
	param		colorNumber	UInt32 in value
	param		index		UInt32 in value
	param		name		Char in array []
	category	ARB_blend_func_extended
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetFragDataIndex(program, name)
	return		Int32
	param		program		UInt32 in value
	param		name		Char in array []
	category	ARB_blend_func_extended
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #79
# ARB_explicit_attrib_location commands
#
###############################################################################

# (none)
newcategory: ARB_explicit_attrib_location

###############################################################################
#
# ARB Extension #80
# ARB_occlusion_query2 commands
#
###############################################################################

# (none)
newcategory: ARB_occlusion_query2

###############################################################################
#
# ARB Extension #81
# ARB_sampler_objects commands
#
###############################################################################

GenSamplers(count, samplers)
	return		void
	param		count		SizeI in value
	param		samplers	UInt32 out array [count]
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteSamplers(count, samplers)
	return		void
	param		count		SizeI in value
	param		samplers	UInt32 in array [count]
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsSampler(sampler)
	return		Boolean
	param		sampler		UInt32 in value
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindSampler(unit, sampler)
	return		void
	param		unit		UInt32 in value
	param		sampler		UInt32 in value
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SamplerParameteri(sampler, pname, param)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		param		Int32 in value
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SamplerParameteriv(sampler, pname, param)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		param		Int32 in array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SamplerParameterf(sampler, pname, param)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		param		Float32 in value
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SamplerParameterfv(sampler, pname, param)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		param		Float32 in array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SamplerParameterIiv(sampler, pname, param)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		param		Int32 in array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SamplerParameterIuiv(sampler, pname, param)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		param		UInt32 in array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetSamplerParameteriv(sampler, pname, params)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetSamplerParameterIiv(sampler, pname, params)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetSamplerParameterfv(sampler, pname, params)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetSamplerParameterIuiv(sampler, pname, params)
	return		void
	param		sampler		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	category	ARB_sampler_objects
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #82
# ARB_shader_bit_encoding commands
#
###############################################################################

# (none)
newcategory: ARB_shader_bit_encoding

###############################################################################
#
# ARB Extension #83
# ARB_texture_rgb10_a2ui commands
#
###############################################################################

# (none)
newcategory: ARB_texture_rgb10_a2ui

###############################################################################
#
# ARB Extension #84
# ARB_texture_swizzle commands
#
###############################################################################

# (none)
newcategory: ARB_texture_swizzle

###############################################################################
#
# ARB Extension #85
# ARB_timer_query commands
#
###############################################################################

QueryCounter(id, target)
	return		void
	param		id		UInt32 in value
	param		target		GLenum in value
	category	ARB_timer_query
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetQueryObjecti64v(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		Int64 out array [COMPSIZE(pname)]
	category	ARB_timer_query
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetQueryObjectui64v(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt64 out array [COMPSIZE(pname)]
	category	ARB_timer_query
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #86
# ARB_vertex_type_2_10_10_10_rev commands
#
###############################################################################

VertexP2ui(type, value)
	return		void
	param		type		GLenum in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexP2uiv(type, value)
	return		void
	param		type		GLenum in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexP3ui(type, value)
	return		void
	param		type		GLenum in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexP3uiv(type, value)
	return		void
	param		type		GLenum in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexP4ui(type, value)
	return		void
	param		type		GLenum in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexP4uiv(type, value)
	return		void
	param		type		GLenum in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP1ui(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP1uiv(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP2ui(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP2uiv(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP3ui(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP3uiv(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP4ui(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordP4uiv(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP1ui(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP1uiv(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP2ui(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP2uiv(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP3ui(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP3uiv(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP4ui(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoordP4uiv(texture, type, coords)
	return		void
	param		texture		GLenum in value
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalP3ui(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalP3uiv(type, coords)
	return		void
	param		type		GLenum in value
	param		coords		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorP3ui(type, color)
	return		void
	param		type		GLenum in value
	param		color		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorP3uiv(type, color)
	return		void
	param		type		GLenum in value
	param		color		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorP4ui(type, color)
	return		void
	param		type		GLenum in value
	param		color		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorP4uiv(type, color)
	return		void
	param		type		GLenum in value
	param		color		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SecondaryColorP3ui(type, color)
	return		void
	param		type		GLenum in value
	param		color		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SecondaryColorP3uiv(type, color)
	return		void
	param		type		GLenum in value
	param		color		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP1ui(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP1uiv(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP2ui(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP2uiv(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP3ui(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP3uiv(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP4ui(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in value
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribP4uiv(index, type, normalized, value)
	return		void
	param		index		UInt32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		value		UInt32 in array [1]
	category	ARB_vertex_type_2_10_10_10_rev
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #87
# ARB_draw_indirect commands
#
###############################################################################

DrawArraysIndirect(mode, indirect)
	return		void
	param		mode		GLenum in value
	param		indirect	Void in array []
	category	ARB_draw_indirect
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawElementsIndirect(mode, type, indirect)
	return		void
	param		mode		GLenum in value
	param		type		GLenum in value
	param		indirect	Void in array []
	category	ARB_draw_indirect
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #88
# ARB_gpu_shader5 commands
#
###############################################################################

# (none)
newcategory: ARB_gpu_shader5

###############################################################################
#
# ARB Extension #89
# ARB_gpu_shader_fp64 commands
#
###############################################################################

Uniform1d(location, x)
	return		void
	param		location	Int32 in value
	param		x		Float64 in value
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2d(location, x, y)
	return		void
	param		location	Int32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3d(location, x, y, z)
	return		void
	param		location	Int32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4d(location, x, y, z, w)
	return		void
	param		location	Int32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1dv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2dv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3dv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4dv(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix2dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix3dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix4dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix2x3dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix2x4dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix3x2dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix3x4dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix4x2dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformMatrix4x3dv(location, count, transpose, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetUniformdv(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		Float64 out array [COMPSIZE(location)]
	category	ARB_gpu_shader_fp64
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #90
# ARB_shader_subroutine commands
#
###############################################################################

GetSubroutineUniformLocation(program, shadertype, name)
	return		Int32
	param		program		UInt32 in value
	param		shadertype	GLenum in value
	param		name		Char in array []
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetSubroutineIndex(program, shadertype, name)
	return		UInt32
	param		program		UInt32 in value
	param		shadertype	GLenum in value
	param		name		Char in array []
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveSubroutineUniformiv(program, shadertype, index, pname, values)
	return		void
	param		program		UInt32 in value
	param		shadertype	GLenum in value
	param		index		UInt32 in value
	param		pname		GLenum in value
	param		values		Int32 out array [COMPSIZE(pname)]
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveSubroutineUniformName(program, shadertype, index, bufsize, length, name)
	return		void
	param		program		UInt32 in value
	param		shadertype	GLenum in value
	param		index		UInt32 in value
	param		bufsize		SizeI in value
	param		length		SizeI out array [1]
	param		name		Char out array [bufsize]
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetActiveSubroutineName(program, shadertype, index, bufsize, length, name)
	return		void
	param		program		UInt32 in value
	param		shadertype	GLenum in value
	param		index		UInt32 in value
	param		bufsize		SizeI in value
	param		length		SizeI out array [1]
	param		name		Char out array [bufsize]
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

UniformSubroutinesuiv(shadertype, count, indices)
	return		void
	param		shadertype	GLenum in value
	param		count		SizeI in value
	param		indices		UInt32 in array [count]
	category	ARB_shader_subroutine
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetUniformSubroutineuiv(shadertype, location, params)
	return		void
	param		shadertype	GLenum in value
	param		location	Int32 in value
	param		params		UInt32 out array [1]
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramStageiv(program, shadertype, pname, values)
	return		void
	param		program		UInt32 in value
	param		shadertype	GLenum in value
	param		pname		GLenum in value
	param		values		Int32 out array [1]
	category	ARB_shader_subroutine
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #91
# ARB_tessellation_shader commands
#
###############################################################################

PatchParameteri(pname, value)
	return		void
	param		pname		GLenum in value
	param		value		Int32 in value
	category	ARB_tessellation_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PatchParameterfv(pname, values)
	return		void
	param		pname		GLenum in value
	param		values		Float32 in array [COMPSIZE(pname)]
	category	ARB_tessellation_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #92
# ARB_texture_buffer_object_rgb32 commands
#
###############################################################################

# (none)
newcategory: ARB_texture_buffer_object_rgb32

###############################################################################
#
# ARB Extension #93
# ARB_transform_feedback2 commands
#
###############################################################################

BindTransformFeedback(target, id)
	return		void
	param		target		GLenum in value
	param		id		UInt32 in value
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteTransformFeedbacks(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 in array [n]
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GenTransformFeedbacks(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 out array [n]
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsTransformFeedback(id)
	return		Boolean
	param		id		UInt32 in value
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PauseTransformFeedback()
	return		void
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ResumeTransformFeedback()
	return		void
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawTransformFeedback(mode, id)
	return		void
	param		mode		GLenum in value
	param		id		UInt32 in value
	category	ARB_transform_feedback2
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #94
# ARB_transform_feedback3 commands
#
###############################################################################

DrawTransformFeedbackStream(mode, id, stream)
	return		void
	param		mode		GLenum in value
	param		id		UInt32 in value
	param		stream		UInt32 in value
	category	ARB_transform_feedback3
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BeginQueryIndexed(target, index, id)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		id		UInt32 in value
	category	ARB_transform_feedback3
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EndQueryIndexed(target, index)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	category	ARB_transform_feedback3
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetQueryIndexediv(target, index, pname, params)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_transform_feedback3
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #95
# ARB_ES2_compatibility commands
#
###############################################################################

ReleaseShaderCompiler()
	return		void
	category	ARB_ES2_compatibility
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ShaderBinary(count, shaders, binaryformat, binary, length)
	return		void
	param		count		SizeI in value
	param		shaders		UInt32 in array [count]
	param		binaryformat	GLenum in value
	param		binary		Void in array [length]
	param		length		SizeI in value
	category	ARB_ES2_compatibility
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetShaderPrecisionFormat(shadertype, precisiontype, range, precision)
	return		void
	param		shadertype	GLenum in value
	param		precisiontype	GLenum in value
	param		range		Int32 out array [2]
	param		precision	Int32 out array [2]
	category	ARB_ES2_compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

DepthRangef(n, f)
	return		void
	param		n		Float32 in value
	param		f		Float32 in value
	category	ARB_ES2_compatibility
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearDepthf(d)
	return		void
	param		d		Float32 in value
	category	ARB_ES2_compatibility
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #96
# ARB_get_program_binary commands
#
###############################################################################

GetProgramBinary(program, bufSize, length, binaryFormat, binary)
	return		void
	param		program		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		binaryFormat	GLenum out array [1]
	param		binary		Void out array [COMPSIZE(length)]
	category	ARB_get_program_binary
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

ProgramBinary(program, binaryFormat, binary, length)
	return		void
	param		program		UInt32 in value
	param		binaryFormat	GLenum in value
	param		binary		Void in array [length]
	param		length		SizeI in value
	category	ARB_get_program_binary
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramParameteri(program, pname, value)
	return		void
	param		program		UInt32 in value
	param		pname		ProgramParameterPName in value
	param		value		Int32 in value
	category	ARB_get_program_binary
	version		3.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# ARB Extension #97
# ARB_separate_shader_objects commands
#
###############################################################################

UseProgramStages(pipeline, stages, program)
	return		void
	param		pipeline	UInt32 in value
	param		stages		GLbitfield in value
	param		program		UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ActiveShaderProgram(pipeline, program)
	return		void
	param		pipeline	UInt32 in value
	param		program		UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

CreateShaderProgramv(type, count, strings)
	return		UInt32
	param		type		GLenum in value
	param		count		SizeI in value
	param		strings		ConstCharPointer in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindProgramPipeline(pipeline)
	return		void
	param		pipeline	UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteProgramPipelines(n, pipelines)
	return		void
	param		n		SizeI in value
	param		pipelines	UInt32 in array [n]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GenProgramPipelines(n, pipelines)
	return		void
	param		n		SizeI in value
	param		pipelines	UInt32 out array [n]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsProgramPipeline(pipeline)
	return		Boolean
	param		pipeline	UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

#@ ProgramParameteri also in ARB_get_program_binary

GetProgramPipelineiv(pipeline, pname, params)
	return		void
	param		pipeline	UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_separate_shader_objects
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

ProgramUniform1i(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1iv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [1]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1f(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1fv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [1]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1d(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float64 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1dv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [1]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1ui(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1uiv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [1]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2i(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2iv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [2]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2f(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2fv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [2]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2d(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float64 in value
	param		v1		Float64 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2dv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [2]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2ui(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2uiv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [2]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3i(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3iv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [3]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3f(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3fv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [3]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3d(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float64 in value
	param		v1		Float64 in value
	param		v2		Float64 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3dv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [3]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3ui(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3uiv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [3]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4i(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	param		v3		Int32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4iv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [4]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4f(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	param		v3		Float32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4fv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [4]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4d(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float64 in value
	param		v1		Float64 in value
	param		v2		Float64 in value
	param		v3		Float64 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4dv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [4]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4ui(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	param		v3		UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4uiv(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [4]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [2]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [3]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [4]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [2]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [3]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [4]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2x3fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3x2fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2x4fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4x2fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3x4fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4x3fv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2x3dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3x2dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2x4dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4x2dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3x4dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4x3dv(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count]
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ValidateProgramPipeline(pipeline)
	return		void
	param		pipeline	UInt32 in value
	category	ARB_separate_shader_objects
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetProgramPipelineInfoLog(pipeline, bufSize, length, infoLog)
	return		void
	param		pipeline	UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		infoLog		Char out array [COMPSIZE(length)]
	category	ARB_separate_shader_objects
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #98
# ARB_shader_precision commands
#
###############################################################################

###############################################################################
#
# ARB Extension #99
# ARB_vertex_attrib_64bit commands
#
###############################################################################

VertexAttribL1d(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2d(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3d(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4d(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL1dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [1]
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [2]
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [3]
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4dv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [4]
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribLPointer(index, size, type, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	param		pointer		Void in array [size]
	category	ARB_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVertexAttribLdv(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		GLenum in value
	param		params		Float64 out array [COMPSIZE(pname)]
	category	ARB_vertex_attrib_64bit
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

#@ VertexArrayVertexAttribLOffsetEXT also in EXT_vertex_attrib_64bit

###############################################################################
#
# ARB Extension #100
# ARB_viewport_array commands
#
###############################################################################

ViewportArrayv(first, count, v)
	return		void
	param		first		UInt32 in value
	param		count		SizeI in value
	param		v		Float32 in array [COMPSIZE(count)]
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ViewportIndexedf(index, x, y, w, h)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		w		Float32 in value
	param		h		Float32 in value
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ViewportIndexedfv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [4]
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ScissorArrayv(first, count, v)
	return		void
	param		first		UInt32 in value
	param		count		SizeI in value
	param		v		Int32 in array [COMPSIZE(count)]
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ScissorIndexed(index, left, bottom, width, height)
	return		void
	param		index		UInt32 in value
	param		left		Int32 in value
	param		bottom		Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ScissorIndexedv(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DepthRangeArrayv(first, count, v)
	return		void
	param		first		UInt32 in value
	param		count		SizeI in value
	param		v		Float64 in array [COMPSIZE(count)]
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DepthRangeIndexed(index, n, f)
	return		void
	param		index		UInt32 in value
	param		n		Float64 in value
	param		f		Float64 in value
	category	ARB_viewport_array
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetFloati_v(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Float32 out array [COMPSIZE(target)]
	category	ARB_viewport_array
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetDoublei_v(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Float64 out array [COMPSIZE(target)]
	category	ARB_viewport_array
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #101 - GLX_ARB_create_context_robustness
# ARB Extension #102 - WGL_ARB_create_context_robustness
#
###############################################################################

###############################################################################
#
# ARB Extension #103
# ARB_cl_event commands
#
###############################################################################

CreateSyncFromCLeventARB(context, event, flags)
	return		sync
	param		context		cl_context in value
	param		event		cl_event in value
	param		flags		GLbitfield in value
	category	ARB_cl_event
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #104
# ARB_debug_output commands
#
###############################################################################

DebugMessageControlARB(source, type, severity, count, ids, enabled)
	return		void
	param		source		GLenum in value
	param		type		GLenum in value
	param		severity	GLenum in value
	param		count		SizeI in value
	param		ids		UInt32 in array [count]
	param		enabled		Boolean in value
	category	ARB_debug_output
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DebugMessageInsertARB(source, type, id, severity, length, buf)
	return		void
	param		source		GLenum in value
	param		type		GLenum in value
	param		id		UInt32 in value
	param		severity	GLenum in value
	param		length		SizeI in value
	param		buf		Char in array [length]
	category	ARB_debug_output
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DebugMessageCallbackARB(callback, userParam)
	return		void
	param		callback	GLDEBUGPROCARB in value
	param		userParam	Void in array [COMPSIZE(callback)]
	category	ARB_debug_output
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetDebugMessageLogARB(count, bufsize, sources, types, ids, severities, lengths, messageLog)
	return		UInt32
	param		count		UInt32 in value
	param		bufsize		SizeI in value
	param		sources		GLenum out array [count]
	param		types		GLenum out array [count]
	param		ids		UInt32 out array [count]
	param		severities	GLenum out array [count]
	param		lengths		SizeI out array [count]
	param		messageLog	Char out array [COMPSIZE(lengths)]
	category	ARB_debug_output
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

# GetPointerv is redeclared in this extension

###############################################################################
#
# ARB Extension #105
# ARB_robustness commands
#
###############################################################################

GetGraphicsResetStatusARB()
	return		GLenum
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnMapdvARB(target, query, bufSize, v)
	return		void
	param		target		GLenum in value
	param		query		GLenum in value
	param		bufSize		SizeI in value
	param		v		Float64 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnMapfvARB(target, query, bufSize, v)
	return		void
	param		target		GLenum in value
	param		query		GLenum in value
	param		bufSize		SizeI in value
	param		v		Float32 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnMapivARB(target, query, bufSize, v)
	return		void
	param		target		GLenum in value
	param		query		GLenum in value
	param		bufSize		SizeI in value
	param		v		Int32 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnPixelMapfvARB(map, bufSize, values)
	return		void
	param		map		GLenum in value
	param		bufSize		SizeI in value
	param		values		Float32 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnPixelMapuivARB(map, bufSize, values)
	return		void
	param		map		GLenum in value
	param		bufSize		SizeI in value
	param		values		UInt32 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnPixelMapusvARB(map, bufSize, values)
	return		void
	param		map		GLenum in value
	param		bufSize		SizeI in value
	param		values		UInt16 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnPolygonStippleARB(bufSize, pattern)
	return		void
	param		bufSize		SizeI in value
	param		pattern		UInt8 out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnColorTableARB(target, format, type, bufSize, table)
	return		void
	param		target		GLenum in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		bufSize		SizeI in value
	param		table		Void out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnConvolutionFilterARB(target, format, type, bufSize, image)
	return		void
	param		target		GLenum in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		bufSize		SizeI in value
	param		image		Void out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnSeparableFilterARB(target, format, type, rowBufSize, row, columnBufSize, column, span)
	return		void
	param		target		GLenum in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		rowBufSize	SizeI in value
	param		row		Void out array [rowBufSize]
	param		columnBufSize	SizeI in value
	param		column		Void out array [columnBufSize]
	param		span		Void out array [0]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnHistogramARB(target, reset, format, type, bufSize, values)
	return		void
	param		target		GLenum in value
	param		reset		Boolean in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		bufSize		SizeI in value
	param		values		Void out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnMinmaxARB(target, reset, format, type, bufSize, values)
	return		void
	param		target		GLenum in value
	param		reset		Boolean in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		bufSize		SizeI in value
	param		values		Void out array [bufSize]
	category	ARB_robustness
	profile		compatibility
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnTexImageARB(target, level, format, type, bufSize, img)
	return		void
	param		target		GLenum in value
	param		level		Int32 in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		bufSize		SizeI in value
	param		img		Void out array [bufSize]
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

ReadnPixelsARB(x, y, width, height, format, type, bufSize, data)
	return		void
	param		x		Int32 in value
	param		y		Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		bufSize		SizeI in value
	param		data		Void out array [bufSize]
	category	ARB_robustness
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetnCompressedTexImageARB(target, lod, bufSize, img)
	return		void
	param		target		GLenum in value
	param		lod		Int32 in value
	param		bufSize		SizeI in value
	param		img		Void out array [bufSize]
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnUniformfvARB(program, location, bufSize, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		bufSize		SizeI in value
	param		params		Float32 out array [bufSize]
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnUniformivARB(program, location, bufSize, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		bufSize		SizeI in value
	param		params		Int32 out array [bufSize]
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnUniformuivARB(program, location, bufSize, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		bufSize		SizeI in value
	param		params		UInt32 out array [bufSize]
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetnUniformdvARB(program, location, bufSize, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		bufSize		SizeI in value
	param		params		Float64 out array [bufSize]
	category	ARB_robustness
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #106
# ARB_shader_stencil_export commands
#
###############################################################################

# (none)
newcategory: ARB_shader_stencil_export

###############################################################################
#
# ARB Extension #107
# ARB_base_instance commands
#
###############################################################################

DrawArraysInstancedBaseInstance(mode, first, count, instancecount, baseinstance)
	return		void
	param		mode		GLenum in value
	param		first		Int32 in value
	param		count		SizeI in value
	param		instancecount	SizeI in value
	param		baseinstance	UInt32 in value
	category	ARB_base_instance
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawElementsInstancedBaseInstance(mode, count, type, indices, instancecount, baseinstance)
	return		void
	param		mode		GLenum in value
	param		count		SizeI in value
	param		type		GLenum in value
	param		indices		void in array [count]
	param		instancecount	SizeI in value
	param		baseinstance	UInt32 in value
	category	ARB_base_instance
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawElementsInstancedBaseVertexBaseInstance(mode, count, type, indices, instancecount, basevertex, baseinstance)
	return		void
	param		mode		GLenum in value
	param		count		SizeI in value
	param		type		GLenum in value
	param		indices		void in array [count]
	param		instancecount	SizeI in value
	param		basevertex	Int32 in value
	param		baseinstance	UInt32 in value
	category	ARB_base_instance
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #108
# ARB_shading_language_420pack commands
#
###############################################################################

# (none)
newcategory: ARB_shading_language_420pack

###############################################################################
#
# ARB Extension #109
# ARB_transform_feedback_instanced commands
#
###############################################################################

DrawTransformFeedbackInstanced(mode, id, instancecount)
	return		void
	param		mode		GLenum in value
	param		id		UInt32 in value
	param		instancecount	SizeI in value
	category	ARB_transform_feedback_instanced
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawTransformFeedbackStreamInstanced(mode, id, stream, instancecount)
	return		void
	param		mode		GLenum in value
	param		id		UInt32 in value
	param		stream		UInt32 in value
	param		instancecount	SizeI in value
	category	ARB_transform_feedback_instanced
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #110
# ARB_compressed_texture_pixel_storage commands
#
###############################################################################

# (none)
newcategory: ARB_compressed_texture_pixel_storage

###############################################################################
#
# ARB Extension #111
# ARB_conservative_depth commands
#
###############################################################################

# (none)
newcategory: ARB_conservative_depth

###############################################################################
#
# ARB Extension #112
# ARB_internalformat_query commands
#
###############################################################################

GetInternalformativ(target, internalformat, pname, bufSize, params)
	return		void
	param		target		GLenum in value
	param		internalformat	GLenum in value
	param		pname		GLenum in value
	param		bufSize		SizeI in value
	param		params		Int32 out array [bufSize]
	category	ARB_internalformat_query
	dlflags		notlistable
	version		4.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #113
# ARB_map_buffer_alignment commands
#
###############################################################################

# (none)
newcategory: ARB_map_buffer_alignment

###############################################################################
#
# ARB Extension #114
# ARB_shader_atomic_counters commands
#
###############################################################################

GetActiveAtomicCounterBufferiv(program, bufferIndex, pname, params)
	return		void
	param		program		UInt32 in value
	param		bufferIndex	UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_shader_atomic_counters
	dlflags		notlistable
	version		4.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #115
# ARB_shader_image_load_store commands
#
###############################################################################

BindImageTexture(unit, texture, level, layered, layer, access, format)
	return		void
	param		unit		UInt32 in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		layered		Boolean in value
	param		layer		Int32 in value
	param		access		GLenum in value
	param		format		GLenum in value
	category	ARB_shader_image_load_store
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MemoryBarrier(barriers)
	return		void
	param		barriers	GLbitfield in value
	category	ARB_shader_image_load_store
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# ARB Extension #116
# ARB_shading_language_packing commands
#
###############################################################################

# (none)
newcategory: ARB_shading_language_packing

###############################################################################
#
# ARB Extension #117
# ARB_texture_storage commands
#
###############################################################################

TexStorage1D(target, levels, internalformat, width)
	return		void
	param		target		GLenum in value
	param		levels		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	category	ARB_texture_storage
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexStorage2D(target, levels, internalformat, width, height)
	return		void
	param		target		GLenum in value
	param		levels		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	ARB_texture_storage
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexStorage3D(target, levels, internalformat, width, height, depth)
	return		void
	param		target		GLenum in value
	param		levels		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	category	ARB_texture_storage
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureStorage1DEXT(texture, target, levels, internalformat, width)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		levels		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	category	ARB_texture_storage
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureStorage2DEXT(texture, target, levels, internalformat, width, height)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		levels		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	ARB_texture_storage
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureStorage3DEXT(texture, target, levels, internalformat, width, height, depth)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		levels		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	category	ARB_texture_storage
	version		4.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB118
# KHR_texture_compression_astc_ldr commands
#
###############################################################################

# (none)
newcategory: KHR_texture_compression_astc_ldr

###############################################################################
#
# Extension #ARB119
# KHR_debug commands
#
###############################################################################

# Promoted from ARB_debug_output
DebugMessageControl(source, type, severity, count, ids, enabled)
	return		void
	param		source		GLenum in value
	param		type		GLenum in value
	param		severity	GLenum in value
	param		count		SizeI in value
	param		ids		UInt32 in array [count]
	param		enabled		Boolean in value
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DebugMessageInsert(source, type, id, severity, length, buf)
	return		void
	param		source		GLenum in value
	param		type		GLenum in value
	param		id		UInt32 in value
	param		severity	GLenum in value
	param		length		SizeI in value
	param		buf		Char in array [COMPSIZE(buf/length)]
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DebugMessageCallback(callback, userParam)
	return		void
	param		callback	GLDEBUGPROC in value
	param		userParam	void in reference
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# bufsize -> logSize? (Bug 9178)
GetDebugMessageLog(count, bufsize, sources, types, ids, severities, lengths, messageLog)
	return		UInt32
	param		count		UInt32 in value
	param		bufsize		SizeI in value
	param		sources		GLenum out array [COMPSIZE(count)]
	param		types		GLenum out array [COMPSIZE(count)]
	param		ids		UInt32 out array [COMPSIZE(count)]
	param		severities	GLenum out array [COMPSIZE(count)]
	param		lengths		SizeI out array [COMPSIZE(count)]
	param		messageLog	Char out array [COMPSIZE(bufsize)]
	category	KHR_debug
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

PushDebugGroup(source, id, length, message)
	return		void
	param		source		GLenum in value
	param		id		UInt32 in value
	param		length		SizeI in value
	param		message		Char in array [COMPSIZE(message/length)]
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PopDebugGroup()
	return		void
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ObjectLabel(identifier, name, length, label)
	return		void
	param		identifier	GLenum in value
	param		name		UInt32 in value
	param		length		SizeI in value
	param		label		Char in array [COMPSIZE(label/length)]
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetObjectLabel(identifier, name, bufSize, length, label)
	return		void
	param		identifier	GLenum in value
	param		name		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out reference
	param		label		Char out array [bufSize]
	category	KHR_debug
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

ObjectPtrLabel(ptr, length, label)
	return		void
	param		ptr		void in reference
	param		length		SizeI in value
	param		label		Char in array [COMPSIZE(label/length)]
	category	KHR_debug
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetObjectPtrLabel(ptr, bufSize, length, label)
	return		void
	param		ptr		void in reference
	param		bufSize		SizeI in value
	param		length		SizeI out reference
	param		label		Char out array [bufSize]
	category	KHR_debug
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

# Also includes GetPointerv (only for OpenGL ES 2, however)

###############################################################################
#
# Extension #ARB120
# ARB_arrays_of_arrays commands
#
###############################################################################

# (none)
newcategory: ARB_arrays_of_arrays

###############################################################################
#
# Extension #ARB121
# ARB_clear_buffer_object commands
#
###############################################################################

ClearBufferData(target, internalformat, format, type, data)
	return		void
	param		target		GLenum in value
	param		internalformat	GLenum in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		data		void in array [COMPSIZE(format/type)]
	category	ARB_clear_buffer_object
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearBufferSubData(target, internalformat, offset, size, format, type, data)
	return		void
	param		target		GLenum in value
	param		internalformat	GLenum in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		data		void in array [COMPSIZE(format/type)]
	category	ARB_clear_buffer_object
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# Only for use with DSA extensions

ClearNamedBufferDataEXT(buffer, internalformat, format, type, data)
	return		void
	param		buffer		UInt32 in value
	param		internalformat	GLenum in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		data		void in array [COMPSIZE(format/type)]
	category	ARB_clear_buffer_object
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearNamedBufferSubDataEXT(buffer, internalformat, format, type, offset, size, data)
	return		void
	param		buffer		UInt32 in value
	param		internalformat	GLenum in value
	param		offset		BufferSize in value
	param		size		BufferSize in value
	param		format		GLenum in value
	param		type		GLenum in value
	param		data		void in array [COMPSIZE(format/type)]
	category	ARB_clear_buffer_object
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB122
# ARB_compute_shader commands
#
###############################################################################

DispatchCompute(num_groups_x, num_groups_y, num_groups_z)
	return		void
	param		num_groups_x	UInt32 in value
	param		num_groups_y	UInt32 in value
	param		num_groups_z	UInt32 in value
	category	ARB_compute_shader
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DispatchComputeIndirect(indirect)
	return		void
	param		indirect	BufferOffset in value
	category	ARB_compute_shader
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB123
# ARB_copy_image commands
#
###############################################################################

CopyImageSubData(srcName, srcTarget, srcLevel, srcX, srcY, srcZ, dstName, dstTarget, dstLevel, dstX, dstY, dstZ, srcWidth, srcHeight, srcDepth)
	return		void
	param		srcName		UInt32 in value
	param		srcTarget	GLenum in value
	param		srcLevel	Int32 in value
	param		srcX		Int32 in value
	param		srcY		Int32 in value
	param		srcZ		Int32 in value
	param		dstName		UInt32 in value
	param		dstTarget	GLenum in value
	param		dstLevel	Int32 in value
	param		dstX		Int32 in value
	param		dstY		Int32 in value
	param		dstZ		Int32 in value
	param		srcWidth	SizeI in value
	param		srcHeight	SizeI in value
	param		srcDepth	SizeI in value
	category	ARB_copy_image
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB124 (renumbered from 142)
# ARB_texture_view commands
#
###############################################################################

TextureView(texture, target, origtexture, internalformat, minlevel, numlevels, minlayer, numlayers)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		origtexture	UInt32 in value
	param		internalformat	GLenum in value
	param		minlevel	UInt32 in value
	param		numlevels	UInt32 in value
	param		minlayer	UInt32 in value
	param		numlayers	UInt32 in value
	category	ARB_texture_view
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB125 (renumbered from 143)
# ARB_vertex_attrib_binding commands
#
###############################################################################

BindVertexBuffer(bindingindex, buffer, offset, stride)
	return		void
	param		bindingindex	UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		stride		SizeI in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribFormat(attribindex, size, type, normalized, relativeoffset)
	return		void
	param		attribindex	UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		relativeoffset	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribIFormat(attribindex, size, type, relativeoffset)
	return		void
	param		attribindex	UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		relativeoffset	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribLFormat(attribindex, size, type, relativeoffset)
	return		void
	param		attribindex	UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		relativeoffset	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribBinding(attribindex, bindingindex)
	return		void
	param		attribindex	UInt32 in value
	param		bindingindex	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexBindingDivisor(bindingindex, divisor)
	return		void
	param		bindingindex	UInt32 in value
	param		divisor		UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayBindVertexBufferEXT(vaobj, bindingindex, buffer, offset, stride)
	return		void
	param		vaobj		UInt32 in value
	param		bindingindex	UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		stride		SizeI in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayVertexAttribFormatEXT(vaobj, attribindex, size, type, normalized, relativeoffset)
	return		void
	param		vaobj		UInt32 in value
	param		attribindex	UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		relativeoffset	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayVertexAttribIFormatEXT(vaobj, attribindex, size, type, relativeoffset)
	return		void
	param		vaobj		UInt32 in value
	param		attribindex	UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		relativeoffset	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayVertexAttribLFormatEXT(vaobj, attribindex, size, type, relativeoffset)
	return		void
	param		vaobj		UInt32 in value
	param		attribindex	UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		relativeoffset	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayVertexAttribBindingEXT(vaobj, attribindex, bindingindex)
	return		void
	param		vaobj		UInt32 in value
	param		attribindex	UInt32 in value
	param		bindingindex	UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayVertexBindingDivisorEXT(vaobj, bindingindex, divisor)
	return		void
	param		vaobj		UInt32 in value
	param		bindingindex	UInt32 in value
	param		divisor		UInt32 in value
	category	ARB_vertex_attrib_binding
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB126 (renumbered from 144)
# ARB_robustness_isolation commands
#
###############################################################################

# (none)
newcategory: ARB_robustness_isolation

###############################################################################
#
# Extension #ARB127
# ARB_ES3_compatibility commands
#
###############################################################################

# (none)
newcategory: ARB_ES3_compatibility

###############################################################################
#
# Extension #ARB128
# ARB_explicit_uniform_location commands
#
###############################################################################

# (none)
newcategory: ARB_explicit_uniform_location

###############################################################################
#
# Extension #ARB129
# ARB_fragment_layer_viewport commands
#
###############################################################################

# (none)
newcategory: ARB_fragment_layer_viewport

###############################################################################
#
# Extension #ARB130
# ARB_framebuffer_no_attachments commands
#
###############################################################################

FramebufferParameteri(target, pname, param)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		param		Int32 in value
	category	ARB_framebuffer_no_attachments
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetFramebufferParameteriv(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_framebuffer_no_attachments
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

NamedFramebufferParameteriEXT(framebuffer, pname, param)
	return		void
	param		framebuffer	UInt32 in value
	param		pname		GLenum in value
	param		param		Int32 in value
	category	ARB_framebuffer_no_attachments
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetNamedFramebufferParameterivEXT(framebuffer, pname, params)
	return		void
	param		framebuffer	UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_framebuffer_no_attachments
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB131
# ARB_internalformat_query2 commands
#
###############################################################################

GetInternalformati64v(target, internalformat, pname, bufSize, params)
	return		void
	param		target		GLenum in value
	param		internalformat	GLenum in value
	param		pname		GLenum in value
	param		bufSize		SizeI in value
	param		params		Int64 out array [bufSize]
	category	ARB_internalformat_query2
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB132
# ARB_invalidate_subdata commands
#
###############################################################################

InvalidateTexSubImage(texture, level, xoffset, yoffset, zoffset, width, height, depth)
	return		void
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		xoffset		Int32 in value
	param		yoffset		Int32 in value
	param		zoffset		Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	category	ARB_invalidate_subdata
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

InvalidateTexImage(texture, level)
	return		void
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	ARB_invalidate_subdata
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

InvalidateBufferSubData(buffer, offset, length)
	return		void
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		length		BufferSize in value
	category	ARB_invalidate_subdata
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

InvalidateBufferData(buffer)
	return		void
	param		buffer		UInt32 in value
	category	ARB_invalidate_subdata
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

InvalidateFramebuffer(target, numAttachments, attachments)
	return		void
	param		target		GLenum in value
	param		numAttachments	SizeI in value
	param		attachments	GLenum in array [numAttachments]
	category	ARB_invalidate_subdata
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

InvalidateSubFramebuffer(target, numAttachments, attachments, x, y, width, height)
	return		void
	param		target		GLenum in value
	param		numAttachments	SizeI in value
	param		attachments	GLenum in array [numAttachments]
	param		x		Int32 in value
	param		y		Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	ARB_invalidate_subdata
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB133
# ARB_multi_draw_indirect commands
#
###############################################################################

MultiDrawArraysIndirect(mode, indirect, drawcount, stride)
	return		void
	param		mode		GLenum in value
	param		indirect	void in array [COMPSIZE(drawcount/stride)]
	param		drawcount	SizeI in value
	param		stride		SizeI in value
	category	ARB_multi_draw_indirect
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiDrawElementsIndirect(mode, type, indirect, drawcount, stride)
	return		void
	param		mode		GLenum in value
	param		type		GLenum in value
	param		indirect	void in array [COMPSIZE(drawcount/stride)]
	param		drawcount	SizeI in value
	param		stride		SizeI in value
	category	ARB_multi_draw_indirect
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB134
# ARB_program_interface_query commands
#
###############################################################################

GetProgramInterfaceiv(program, programInterface, pname, params)
	return		void
	param		program		UInt32 in value
	param		programInterface	GLenum in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	ARB_program_interface_query
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramResourceIndex(program, programInterface, name)
	return		UInt32
	param		program		UInt32 in value
	param		programInterface	GLenum in value
	param		name		Char in array [COMPSIZE(name)]
	category	ARB_program_interface_query
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramResourceName(program, programInterface, index, bufSize, length, name)
	return		void
	param		program		UInt32 in value
	param		programInterface	GLenum in value
	param		index		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out reference
	param		name		Char out array [bufSize]
	category	ARB_program_interface_query
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramResourceiv(program, programInterface, index, propCount, props, bufSize, length, params)
	return		void
	param		program		UInt32 in value
	param		programInterface	GLenum in value
	param		index		UInt32 in value
	param		propCount	SizeI in value
	param		props		GLenum in array [propCount]
	param		bufSize		SizeI in value
	param		length		SizeI out reference
	param		params		Int32 out array [bufSize]
	category	ARB_program_interface_query
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramResourceLocation(program, programInterface, name)
	return		Int32
	param		program		UInt32 in value
	param		programInterface	GLenum in value
	param		name		Char in array [COMPSIZE(name)]
	category	ARB_program_interface_query
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetProgramResourceLocationIndex(program, programInterface, name)
	return		Int32
	param		program		UInt32 in value
	param		programInterface	GLenum in value
	param		name		Char in array [COMPSIZE(name)]
	category	ARB_program_interface_query
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB135
# ARB_robust_buffer_access_behavior commands
#
###############################################################################

# (none)
newcategory: ARB_robust_buffer_access_behavior

###############################################################################
#
# Extension #ARB136
# ARB_shader_image_size commands
#
###############################################################################

# (none)
newcategory: ARB_shader_image_size

###############################################################################
#
# Extension #ARB137
# ARB_shader_storage_buffer_object commands
#
###############################################################################

ShaderStorageBlockBinding(program, storageBlockIndex, storageBlockBinding)
	return		void
	param		program		UInt32 in value
	param		storageBlockIndex	UInt32 in value
	param		storageBlockBinding	UInt32 in value
	category	ARB_shader_storage_buffer_object
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB138
# ARB_stencil_texturing commands
#
###############################################################################

# (none)
newcategory: ARB_stencil_texturing

###############################################################################
#
# Extension #ARB139
# ARB_texture_buffer_range commands
#
###############################################################################

TexBufferRange(target, internalformat, buffer, offset, size)
	return		void
	param		target		GLenum in value
	param		internalformat	GLenum in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	category	ARB_texture_buffer_range
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureBufferRangeEXT(texture, target, internalformat, buffer, offset, size)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		internalformat	GLenum in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	category	ARB_texture_buffer_range
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #ARB140
# ARB_texture_query_levels commands
#
###############################################################################

# (none)
newcategory: ARB_texture_query_levels

###############################################################################
#
# Extension #ARB141
# ARB_texture_storage_multisample commands
#
###############################################################################

TexStorage2DMultisample(target, samples, internalformat, width, height, fixedsamplelocations)
	return		void
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		fixedsamplelocations	Boolean in value
	category	ARB_texture_storage_multisample
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexStorage3DMultisample(target, samples, internalformat, width, height, depth, fixedsamplelocations)
	return		void
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		fixedsamplelocations	Boolean in value
	category	ARB_texture_storage_multisample
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureStorage2DMultisampleEXT(texture, target, samples, internalformat, width, height, fixedsamplelocations)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		fixedsamplelocations	Boolean in value
	category	ARB_texture_storage_multisample
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureStorage3DMultisampleEXT(texture, target, samples, internalformat, width, height, depth, fixedsamplelocations)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		fixedsamplelocations	Boolean in value
	category	ARB_texture_storage_multisample
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?


###############################################################################
###############################################################################
#
# Non-ARB extensions, in order by registry extension number
#
###############################################################################
###############################################################################

###############################################################################
#
# Extension #1
# EXT_abgr commands
#
###############################################################################

# (none)
newcategory: EXT_abgr

###############################################################################
#
# Extension #2
# EXT_blend_color commands
#
###############################################################################

BlendColorEXT(red, green, blue, alpha)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	param		alpha		ColorF in value
	category	EXT_blend_color
	version		1.0
	glxropcode	4096
	glxflags	EXT
	extension	soft
	alias		BlendColor

###############################################################################
#
# Extension #3
# EXT_polygon_offset commands
#
###############################################################################

PolygonOffsetEXT(factor, bias)
	return		void
	param		factor		Float32 in value
	param		bias		Float32 in value
	category	EXT_polygon_offset
	version		1.0
	glxropcode	4098
	glxflags	EXT
	extension	soft
	offset		414

###############################################################################
#
# Extension #4
# EXT_texture commands
#
###############################################################################

# (none)
newcategory: EXT_texture

###############################################################################
#
# Extension #5 - skipped
#
###############################################################################

###############################################################################
#
# Extension #6
# EXT_texture3D commands
#
###############################################################################

# Arguably TexelInternalFormat, not PixelInternalFormat
TexImage3DEXT(target, level, internalformat, width, height, depth, border, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	EXT_texture3D
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4114
	extension
	alias		TexImage3D

TexSubImage3DEXT(target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	EXT_texture3D
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4115
	extension
	alias		TexSubImage3D

###############################################################################
#
# Extension #7
# SGIS_texture_filter4 commands
#
###############################################################################

GetTexFilterFuncSGIS(target, filter, weights)
	return		void
	param		target		TextureTarget in value
	param		filter		TextureFilterSGIS in value
	param		weights		Float32 out array [COMPSIZE(target/filter)]
	category	SGIS_texture_filter4
	dlflags		notlistable
	version		1.0
	glxflags	SGI
	glxvendorpriv	4101
	extension
	offset		415

TexFilterFuncSGIS(target, filter, n, weights)
	return		void
	param		target		TextureTarget in value
	param		filter		TextureFilterSGIS in value
	param		n		SizeI in value
	param		weights		Float32 in array [n]
	category	SGIS_texture_filter4
	glxflags	SGI
	version		1.0
	glxropcode	2064
	extension
	offset		416

###############################################################################
#
# Extension #8 - skipped
#
###############################################################################

###############################################################################
#
# Extension #9
# EXT_subtexture commands
#
###############################################################################

TexSubImage1DEXT(target, level, xoffset, width, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	EXT_subtexture
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4099
	extension
	alias		TexSubImage1D

TexSubImage2DEXT(target, level, xoffset, yoffset, width, height, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	EXT_subtexture
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4100
	extension
	alias		TexSubImage2D

###############################################################################
#
# Extension #10
# EXT_copy_texture commands
#
###############################################################################

# Arguably TexelInternalFormat, not PixelInternalFormat
CopyTexImage1DEXT(target, level, internalformat, x, y, width, border)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	category	EXT_copy_texture
	version		1.0
	glxflags	EXT
	glxropcode	4119
	extension
	alias		CopyTexImage1D

# Arguably TexelInternalFormat, not PixelInternalFormat
CopyTexImage2DEXT(target, level, internalformat, x, y, width, height, border)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	category	EXT_copy_texture
	version		1.0
	glxflags	EXT
	glxropcode	4120
	extension
	alias		CopyTexImage2D

CopyTexSubImage1DEXT(target, level, xoffset, x, y, width)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	EXT_copy_texture
	version		1.0
	glxflags	EXT
	glxropcode	4121
	extension
	alias		CopyTexSubImage1D

CopyTexSubImage2DEXT(target, level, xoffset, yoffset, x, y, width, height)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_copy_texture
	version		1.0
	glxflags	EXT
	glxropcode	4122
	extension
	alias		CopyTexSubImage2D

CopyTexSubImage3DEXT(target, level, xoffset, yoffset, zoffset, x, y, width, height)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_copy_texture
	version		1.0
	glxflags	EXT
	glxropcode	4123
	extension
	alias		CopyTexSubImage3D

###############################################################################
#
# Extension #11
# EXT_histogram commands
#
###############################################################################

GetHistogramEXT(target, reset, format, type, values)
	return		void
	param		target		HistogramTargetEXT in value
	param		reset		Boolean in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		values		Void out array [COMPSIZE(target/format/type)]
	category	EXT_histogram
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxvendorpriv	5
	extension
	offset		417

GetHistogramParameterfvEXT(target, pname, params)
	return		void
	param		target		HistogramTargetEXT in value
	param		pname		GetHistogramParameterPNameEXT in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_histogram
	dlflags		notlistable
	version		1.0
	glxvendorpriv	6
	glxflags	EXT
	extension
	offset		418

GetHistogramParameterivEXT(target, pname, params)
	return		void
	param		target		HistogramTargetEXT in value
	param		pname		GetHistogramParameterPNameEXT in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_histogram
	dlflags		notlistable
	version		1.0
	glxvendorpriv	7
	glxflags	EXT
	extension
	offset		419

GetMinmaxEXT(target, reset, format, type, values)
	return		void
	param		target		MinmaxTargetEXT in value
	param		reset		Boolean in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		values		Void out array [COMPSIZE(target/format/type)]
	category	EXT_histogram
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxvendorpriv	8
	extension
	offset		420

GetMinmaxParameterfvEXT(target, pname, params)
	return		void
	param		target		MinmaxTargetEXT in value
	param		pname		GetMinmaxParameterPNameEXT in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_histogram
	dlflags		notlistable
	version		1.0
	glxvendorpriv	9
	glxflags	EXT
	extension
	offset		421

GetMinmaxParameterivEXT(target, pname, params)
	return		void
	param		target		MinmaxTargetEXT in value
	param		pname		GetMinmaxParameterPNameEXT in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_histogram
	dlflags		notlistable
	version		1.0
	glxvendorpriv	10
	glxflags	EXT
	extension
	offset		422

HistogramEXT(target, width, internalformat, sink)
	return		void
	param		target		HistogramTargetEXT in value
	param		width		SizeI in value
	param		internalformat	PixelInternalFormat in value
	param		sink		Boolean in value
	category	EXT_histogram
	version		1.0
	glxropcode	4110
	glxflags	EXT
	extension
	alias		Histogram

MinmaxEXT(target, internalformat, sink)
	return		void
	param		target		MinmaxTargetEXT in value
	param		internalformat	PixelInternalFormat in value
	param		sink		Boolean in value
	category	EXT_histogram
	version		1.0
	glxropcode	4111
	glxflags	EXT
	extension
	alias		Minmax

ResetHistogramEXT(target)
	return		void
	param		target		HistogramTargetEXT in value
	category	EXT_histogram
	version		1.0
	glxropcode	4112
	glxflags	EXT
	extension
	alias		ResetHistogram

ResetMinmaxEXT(target)
	return		void
	param		target		MinmaxTargetEXT in value
	category	EXT_histogram
	version		1.0
	glxropcode	4113
	glxflags	EXT
	extension
	alias		ResetMinmax

###############################################################################
#
# Extension #12
# EXT_convolution commands
#
###############################################################################

ConvolutionFilter1DEXT(target, internalformat, width, format, type, image)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		image		Void in array [COMPSIZE(format/type/width)]
	category	EXT_convolution
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4101
	extension
	alias		ConvolutionFilter1D

ConvolutionFilter2DEXT(target, internalformat, width, height, format, type, image)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		image		Void in array [COMPSIZE(format/type/width/height)]
	category	EXT_convolution
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4102
	extension
	alias		ConvolutionFilter2D

ConvolutionParameterfEXT(target, pname, params)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		pname		ConvolutionParameterEXT in value
	param		params		CheckedFloat32 in value
	category	EXT_convolution
	version		1.0
	glxropcode	4103
	glxflags	EXT
	extension
	alias		ConvolutionParameterf

ConvolutionParameterfvEXT(target, pname, params)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		pname		ConvolutionParameterEXT in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	EXT_convolution
	version		1.0
	glxropcode	4104
	glxflags	EXT
	extension
	alias		ConvolutionParameterfv

ConvolutionParameteriEXT(target, pname, params)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		pname		ConvolutionParameterEXT in value
	param		params		CheckedInt32 in value
	category	EXT_convolution
	version		1.0
	glxropcode	4105
	glxflags	EXT
	extension
	alias		ConvolutionParameteri

ConvolutionParameterivEXT(target, pname, params)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		pname		ConvolutionParameterEXT in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_convolution
	version		1.0
	glxropcode	4106
	glxflags	EXT
	extension
	alias		ConvolutionParameteriv

CopyConvolutionFilter1DEXT(target, internalformat, x, y, width)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	EXT_convolution
	version		1.0
	glxropcode	4107
	glxflags	EXT
	extension
	alias		CopyConvolutionFilter1D

CopyConvolutionFilter2DEXT(target, internalformat, x, y, width, height)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_convolution
	version		1.0
	glxropcode	4108
	glxflags	EXT
	extension
	alias		CopyConvolutionFilter2D

GetConvolutionFilterEXT(target, format, type, image)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		image		Void out array [COMPSIZE(target/format/type)]
	category	EXT_convolution
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxvendorpriv	1
	extension
	offset		423

GetConvolutionParameterfvEXT(target, pname, params)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		pname		ConvolutionParameterEXT in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_convolution
	dlflags		notlistable
	version		1.0
	glxvendorpriv	2
	glxflags	EXT
	extension
	offset		424

GetConvolutionParameterivEXT(target, pname, params)
	return		void
	param		target		ConvolutionTargetEXT in value
	param		pname		ConvolutionParameterEXT in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_convolution
	dlflags		notlistable
	version		1.0
	glxvendorpriv	3
	glxflags	EXT
	extension
	offset		425

GetSeparableFilterEXT(target, format, type, row, column, span)
	return		void
	param		target		SeparableTargetEXT in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		row		Void out array [COMPSIZE(target/format/type)]
	param		column		Void out array [COMPSIZE(target/format/type)]
	param		span		Void out array [COMPSIZE(target/format/type)]
	category	EXT_convolution
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxvendorpriv	4
	extension
	offset		426

SeparableFilter2DEXT(target, internalformat, width, height, format, type, row, column)
	return		void
	param		target		SeparableTargetEXT in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		row		Void in array [COMPSIZE(target/format/type/width)]
	param		column		Void in array [COMPSIZE(target/format/type/height)]
	category	EXT_convolution
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4109
	extension
	alias		SeparableFilter2D

###############################################################################
#
# Extension #13
# SGI_color_matrix commands
#
###############################################################################

# (none)
newcategory: SGI_color_matrix

###############################################################################
#
# Extension #14
# SGI_color_table commands
#
###############################################################################

ColorTableSGI(target, internalformat, width, format, type, table)
	return		void
	param		target		ColorTableTargetSGI in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		table		Void in array [COMPSIZE(format/type/width)]
	category	SGI_color_table
	dlflags		handcode
	glxflags	client-handcode server-handcode SGI
	version		1.0
	glxropcode	2053
	extension
	alias		ColorTable

ColorTableParameterfvSGI(target, pname, params)
	return		void
	param		target		ColorTableTargetSGI in value
	param		pname		ColorTableParameterPNameSGI in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGI_color_table
	version		1.0
	glxropcode	2054
	glxflags	SGI
	extension
	alias		ColorTableParameterfv

ColorTableParameterivSGI(target, pname, params)
	return		void
	param		target		ColorTableTargetSGI in value
	param		pname		ColorTableParameterPNameSGI in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	SGI_color_table
	version		1.0
	glxropcode	2055
	glxflags	SGI
	extension
	alias		ColorTableParameteriv

CopyColorTableSGI(target, internalformat, x, y, width)
	return		void
	param		target		ColorTableTargetSGI in value
	param		internalformat	PixelInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	SGI_color_table
	version		1.0
	glxropcode	2056
	glxflags	SGI
	extension
	alias		CopyColorTable

GetColorTableSGI(target, format, type, table)
	return		void
	param		target		ColorTableTargetSGI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		table		Void out array [COMPSIZE(target/format/type)]
	category	SGI_color_table
	dlflags		notlistable
	glxflags	client-handcode server-handcode SGI
	version		1.0
	glxvendorpriv	4098
	extension
	offset		427

GetColorTableParameterfvSGI(target, pname, params)
	return		void
	param		target		ColorTableTargetSGI in value
	param		pname		GetColorTableParameterPNameSGI in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	SGI_color_table
	dlflags		notlistable
	version		1.0
	glxflags	SGI
	glxvendorpriv	4099
	extension
	offset		428

GetColorTableParameterivSGI(target, pname, params)
	return		void
	param		target		ColorTableTargetSGI in value
	param		pname		GetColorTableParameterPNameSGI in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	SGI_color_table
	dlflags		notlistable
	version		1.0
	glxflags	SGI
	glxvendorpriv	4100
	extension
	offset		429

###############################################################################
#
# Extension #15
# SGIX_pixel_texture commands
#
###############################################################################

PixelTexGenSGIX(mode)
	return		void
	param		mode		PixelTexGenModeSGIX in value
	category	SGIX_pixel_texture
	version		1.0
	glxflags	SGI
	glxropcode	2059
	extension
	offset		430

###############################################################################
#
# Extension #15 (variant)
# SGIS_pixel_texture commands
# Both SGIS and SGIX forms have extension #15!
#
###############################################################################

PixelTexGenParameteriSGIS(pname, param)
	return		void
	param		pname		PixelTexGenParameterNameSGIS in value
	param		param		CheckedInt32 in value
	category	SGIS_pixel_texture
	version		1.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		431

PixelTexGenParameterivSGIS(pname, params)
	return		void
	param		pname		PixelTexGenParameterNameSGIS in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	SGIS_pixel_texture
	version		1.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		432

PixelTexGenParameterfSGIS(pname, param)
	return		void
	param		pname		PixelTexGenParameterNameSGIS in value
	param		param		CheckedFloat32 in value
	category	SGIS_pixel_texture
	version		1.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		433

PixelTexGenParameterfvSGIS(pname, params)
	return		void
	param		pname		PixelTexGenParameterNameSGIS in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGIS_pixel_texture
	version		1.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		434

GetPixelTexGenParameterivSGIS(pname, params)
	return		void
	param		pname		PixelTexGenParameterNameSGIS in value
	param		params		CheckedInt32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	SGIS_pixel_texture
	version		1.0
	extension
	glxvendorpriv	?
	glxflags	ignore
	offset		435

GetPixelTexGenParameterfvSGIS(pname, params)
	return		void
	param		pname		PixelTexGenParameterNameSGIS in value
	param		params		CheckedFloat32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	SGIS_pixel_texture
	version		1.0
	extension
	glxvendorpriv	?
	glxflags	ignore
	offset		436

###############################################################################
#
# Extension #16
# SGIS_texture4D commands
#
###############################################################################

TexImage4DSGIS(target, level, internalformat, width, height, depth, size4d, border, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		size4d		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth/size4d)]
	category	SGIS_texture4D
	dlflags		handcode
	glxflags	client-handcode server-handcode SGI
	version		1.0
	glxropcode	2057
	extension
	offset		437

TexSubImage4DSGIS(target, level, xoffset, yoffset, zoffset, woffset, width, height, depth, size4d, format, type, pixels)
	return		void
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		woffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		size4d		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth/size4d)]
	category	SGIS_texture4D
	dlflags		handcode
	glxflags	client-handcode server-handcode SGI
	version		1.0
	glxropcode	2058
	extension
	offset		438

###############################################################################
#
# Extension #17
# SGI_texture_color_table commands
#
###############################################################################

# (none)
newcategory: SGI_texture_color_table

###############################################################################
#
# Extension #18
# EXT_cmyka commands
#
###############################################################################

# (none)
newcategory: EXT_cmyka

###############################################################################
#
# Extension #19 - skipped
#
###############################################################################

###############################################################################
#
# Extension #20
# EXT_texture_object commands
#
###############################################################################

AreTexturesResidentEXT(n, textures, residences)
	return		Boolean
	param		n		SizeI in value
	param		textures	Texture in array [n]
	param		residences	Boolean out array [n]
	category	EXT_texture_object
	glxflags	EXT
	glxvendorpriv	11
	dlflags		notlistable
	version		1.0
	extension
	offset		439

BindTextureEXT(target, texture)
	return		void
	param		target	TextureTarget in value
	param		texture Texture in value
	category	EXT_texture_object
	version		1.0
	glxflags	EXT
	glxropcode	4117
	extension
	alias		BindTexture

DeleteTexturesEXT(n, textures)
	return		void
	param		n		SizeI in value
	param		textures	Texture in array [n]
	category	EXT_texture_object
	dlflags		notlistable
	version		1.0
	glxflags	EXT
	glxvendorpriv	12
	extension
	offset		561

GenTexturesEXT(n, textures)
	return		void
	param		n		SizeI in value
	param		textures	Texture out array [n]
	category	EXT_texture_object
	dlflags		notlistable
	version		1.0
	glxflags	EXT
	glxvendorpriv	13
	extension
	offset		440

IsTextureEXT(texture)
	return		Boolean
	param		texture Texture in value
	category	EXT_texture_object
	dlflags		notlistable
	version		1.0
	glxflags	EXT
	glxvendorpriv	14
	extension
	offset		441

PrioritizeTexturesEXT(n, textures, priorities)
	return		void
	param		n		SizeI in value
	param		textures	Texture in array [n]
	param		priorities	ClampedFloat32 in array [n]
	category	EXT_texture_object
	glxflags	EXT
	version		1.0
	glxropcode	4118
	extension
	alias		PrioritizeTextures

###############################################################################
#
# Extension #21
# SGIS_detail_texture commands
#
###############################################################################

DetailTexFuncSGIS(target, n, points)
	return		void
	param		target		TextureTarget in value
	param		n		SizeI in value
	param		points		Float32 in array [n*2]
	category	SGIS_detail_texture
	glxflags	SGI
	version		1.0
	glxropcode	2051
	extension
	offset		442

GetDetailTexFuncSGIS(target, points)
	return		void
	param		target		TextureTarget in value
	param		points		Float32 out array [COMPSIZE(target)]
	category	SGIS_detail_texture
	dlflags		notlistable
	version		1.0
	glxflags	SGI
	glxvendorpriv	4096
	extension
	offset		443

###############################################################################
#
# Extension #22
# SGIS_sharpen_texture commands
#
###############################################################################

SharpenTexFuncSGIS(target, n, points)
	return		void
	param		target		TextureTarget in value
	param		n		SizeI in value
	param		points		Float32 in array [n*2]
	category	SGIS_sharpen_texture
	glxflags	SGI
	version		1.0
	glxropcode	2052
	extension
	offset		444

GetSharpenTexFuncSGIS(target, points)
	return		void
	param		target		TextureTarget in value
	param		points		Float32 out array [COMPSIZE(target)]
	category	SGIS_sharpen_texture
	dlflags		notlistable
	version		1.0
	glxflags	SGI
	glxvendorpriv	4097
	extension
	offset		445

###############################################################################
#
# EXT_packed_pixels commands
# Extension #23
#
###############################################################################

# (none)
newcategory: EXT_packed_pixels

###############################################################################
#
# Extension #24
# SGIS_texture_lod commands
#
###############################################################################

# (none)
newcategory: SGIS_texture_lod

###############################################################################
#
# Extension #25
# SGIS_multisample commands
#
###############################################################################

SampleMaskSGIS(value, invert)
	return		void
	param		value		ClampedFloat32 in value
	param		invert		Boolean in value
	category	SGIS_multisample
	version		1.1
	glxropcode	2048
	glxflags	SGI
	extension
	alias		SampleMaskEXT

SamplePatternSGIS(pattern)
	return		void
	param		pattern		SamplePatternSGIS in value
	category	SGIS_multisample
	version		1.0
	glxropcode	2049
	glxflags	SGI
	extension
	alias		SamplePatternEXT

###############################################################################
#
# Extension #26 - no specification?
#
###############################################################################

###############################################################################
#
# Extension #27
# EXT_rescale_normal commands
#
###############################################################################

# (none)
newcategory: EXT_rescale_normal

###############################################################################
#
# Extension #28 - GLX_EXT_visual_info
# Extension #29 - skipped
#
###############################################################################

###############################################################################
#
# Extension #30
# EXT_vertex_array commands
#
###############################################################################

ArrayElementEXT(i)
	return		void
	param		i		Int32 in value
	category	EXT_vertex_array
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	alias		ArrayElement

ColorPointerEXT(size, type, stride, count, pointer)
	return		void
	param		size		Int32 in value
	param		type		ColorPointerType in value
	param		stride		SizeI in value
	param		count		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride/count)] retained
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	offset		448

DrawArraysEXT(mode, first, count)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in value
	param		count		SizeI in value
	category	EXT_vertex_array
	dlflags		handcode
	glxflags	client-handcode server-handcode EXT
	version		1.0
	glxropcode	4116
	extension
	alias		DrawArrays

EdgeFlagPointerEXT(stride, count, pointer)
	return		void
	param		stride		SizeI in value
	param		count		SizeI in value
	param		pointer		Boolean in array [COMPSIZE(stride/count)] retained
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	offset		449

GetPointervEXT(pname, params)
	return		void
	param		pname		GetPointervPName in value
	param		params		VoidPointer out array [1]
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	alias		GetPointerv

IndexPointerEXT(type, stride, count, pointer)
	return		void
	param		type		IndexPointerType in value
	param		stride		SizeI in value
	param		count		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride/count)] retained
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	offset		450

NormalPointerEXT(type, stride, count, pointer)
	return		void
	param		type		NormalPointerType in value
	param		stride		SizeI in value
	param		count		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride/count)] retained
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	offset		451

TexCoordPointerEXT(size, type, stride, count, pointer)
	return		void
	param		size		Int32 in value
	param		type		TexCoordPointerType in value
	param		stride		SizeI in value
	param		count		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride/count)] retained
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	offset		452

VertexPointerEXT(size, type, stride, count, pointer)
	return		void
	param		size		Int32 in value
	param		type		VertexPointerType in value
	param		stride		SizeI in value
	param		count		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride/count)] retained
	category	EXT_vertex_array
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.0
	extension
	offset		453

###############################################################################
#
# Extension #31
# EXT_misc_attribute commands
#
###############################################################################

# (none)
newcategory: EXT_misc_attribute

###############################################################################
#
# Extension #32
# SGIS_generate_mipmap commands
#
###############################################################################

# (none)
newcategory: SGIS_generate_mipmap

###############################################################################
#
# Extension #33
# SGIX_clipmap commands
#
###############################################################################

# (none)
newcategory: SGIX_clipmap

###############################################################################
#
# Extension #34
# SGIX_shadow commands
#
###############################################################################

# (none)
newcategory: SGIX_shadow

###############################################################################
#
# Extension #35
# SGIS_texture_edge_clamp commands
#
###############################################################################

# (none)
newcategory: SGIS_texture_edge_clamp

###############################################################################
#
# Extension #36
# SGIS_texture_border_clamp commands
#
###############################################################################

# (none)
newcategory: SGIS_texture_border_clamp

###############################################################################
#
# Extension #37
# EXT_blend_minmax commands
#
###############################################################################

BlendEquationEXT(mode)
	return		void
	param		mode		BlendEquationModeEXT in value
	category	EXT_blend_minmax
	version		1.0
	glxropcode	4097
	glxflags	EXT
	extension	soft
	alias		BlendEquation

###############################################################################
#
# Extension #38
# EXT_blend_subtract commands
#
###############################################################################

# (none)
newcategory: EXT_blend_subtract

###############################################################################
#
# Extension #39
# EXT_blend_logic_op commands
#
###############################################################################

# (none)
newcategory: EXT_blend_logic_op

###############################################################################
#
# Extension #40 - GLX_SGI_swap_control
# Extension #41 - GLX_SGI_video_sync
# Extension #42 - GLX_SGI_make_current_read
# Extension #43 - GLX_SGIX_video_source
# Extension #44 - GLX_EXT_visual_rating
#
###############################################################################

###############################################################################
#
# Extension #45
# SGIX_interlace commands
#
###############################################################################

# (none)
newcategory: SGIX_interlace

###############################################################################
#
# Extension #46
# SGIX_pixel_tiles commands
#
###############################################################################

# (none)
newcategory: SGIX_pixel_tiles

###############################################################################
#
# Extension #47 - GLX_EXT_import_context
# Extension #48 - skipped
# Extension #49 - GLX_SGIX_fbconfig
# Extension #50 - GLX_SGIX_pbuffer
#
###############################################################################

###############################################################################
#
# Extension #51
# SGIS_texture_select commands
#
# This used to be SGIX_texture_select, which was inconsistent with
# enumext.spec and wrong according to the SGI extension spec.
#
###############################################################################

# (none)
newcategory: SGIS_texture_select
passthru: /* This used to be SGIX prefix, which was an error in the header */

###############################################################################
#
# Extension #52
# SGIX_sprite commands
#
###############################################################################

SpriteParameterfSGIX(pname, param)
	return		void
	param		pname		SpriteParameterNameSGIX in value
	param		param		CheckedFloat32 in value
	category	SGIX_sprite
	version		1.0
	glxflags	SGI
	glxropcode	2060
	extension
	offset		454

SpriteParameterfvSGIX(pname, params)
	return		void
	param		pname		SpriteParameterNameSGIX in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGIX_sprite
	version		1.0
	glxflags	SGI
	glxropcode	2061
	extension
	offset		455

SpriteParameteriSGIX(pname, param)
	return		void
	param		pname		SpriteParameterNameSGIX in value
	param		param		CheckedInt32 in value
	category	SGIX_sprite
	version		1.0
	glxflags	SGI
	glxropcode	2062
	extension
	offset		456

SpriteParameterivSGIX(pname, params)
	return		void
	param		pname		SpriteParameterNameSGIX in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	SGIX_sprite
	version		1.0
	glxflags	SGI
	glxropcode	2063
	extension
	offset		457

###############################################################################
#
# Extension #53
# SGIX_texture_multi_buffer commands
#
###############################################################################

# (none)
newcategory: SGIX_texture_multi_buffer

###############################################################################
#
# Extension #54
# EXT_point_parameters / SGIS_point_parameters commands
#
###############################################################################

PointParameterfEXT(pname, param)
	return		void
	param		pname		PointParameterNameARB in value
	param		param		CheckedFloat32 in value
	category	EXT_point_parameters
	version		1.0
	glxflags	SGI
	extension
	alias		PointParameterfARB

PointParameterfvEXT(pname, params)
	return		void
	param		pname		PointParameterNameARB in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	EXT_point_parameters
	version		1.0
	glxflags	SGI
	extension
	alias		PointParameterfvARB

PointParameterfSGIS(pname, param)
	return		void
	param		pname		PointParameterNameARB in value
	param		param		CheckedFloat32 in value
	category	SGIS_point_parameters
	version		1.0
	glxflags	SGI
	extension
	alias		PointParameterfARB

PointParameterfvSGIS(pname, params)
	return		void
	param		pname		PointParameterNameARB in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGIS_point_parameters
	version		1.0
	glxflags	SGI
	extension
	alias		PointParameterfvARB

###############################################################################
#
# Extension #55
# SGIX_instruments commands
#
###############################################################################

GetInstrumentsSGIX()
	return		Int32
	dlflags		notlistable
	category	SGIX_instruments
	version		1.0
	glxflags	SGI
	glxvendorpriv	4102
	extension
	offset		460

InstrumentsBufferSGIX(size, buffer)
	return		void
	param		size		SizeI in value
	param		buffer		Int32 out array [size] retained
	dlflags		notlistable
	category	SGIX_instruments
	version		1.0
	glxflags	SGI
	glxvendorpriv	4103
	extension
	offset		461

PollInstrumentsSGIX(marker_p)
	return		Int32
	param		marker_p	Int32 out array [1]
	dlflags		notlistable
	category	SGIX_instruments
	version		1.0
	glxflags	SGI
	glxvendorpriv	4104
	extension
	offset		462

ReadInstrumentsSGIX(marker)
	return		void
	param		marker		Int32 in value
	category	SGIX_instruments
	version		1.0
	glxflags	SGI
	glxropcode	2077
	extension
	offset		463

StartInstrumentsSGIX()
	return		void
	category	SGIX_instruments
	version		1.0
	glxflags	SGI
	glxropcode	2069
	extension
	offset		464

StopInstrumentsSGIX(marker)
	return		void
	param		marker		Int32 in value
	category	SGIX_instruments
	version		1.0
	glxflags	SGI
	glxropcode	2070
	extension
	offset		465

###############################################################################
#
# Extension #56
# SGIX_texture_scale_bias commands
#
###############################################################################

# (none)
newcategory: SGIX_texture_scale_bias

###############################################################################
#
# Extension #57
# SGIX_framezoom commands
#
###############################################################################

FrameZoomSGIX(factor)
	return		void
	param		factor		CheckedInt32 in value
	category	SGIX_framezoom
	version		1.0
	glxflags	SGI
	glxropcode	2072
	extension
	offset		466

###############################################################################
#
# Extension #58
# SGIX_tag_sample_buffer commands
#
###############################################################################

TagSampleBufferSGIX()
	return		void
	category	SGIX_tag_sample_buffer
	version		1.0
	glxropcode	2050
	glxflags	SGI
	extension
	offset		467

###############################################################################
#
# Extension #59
# SGIX_polynomial_ffd commands
#
###############################################################################

DeformationMap3dSGIX(target, u1, u2, ustride, uorder, v1, v2, vstride, vorder, w1, w2, wstride, worder, points)
	return		void
	param		target		FfdTargetSGIX in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	param		ustride		Int32 in value
	param		uorder		CheckedInt32 in value
	param		v1		CoordD in value
	param		v2		CoordD in value
	param		vstride		Int32 in value
	param		vorder		CheckedInt32 in value
	param		w1		CoordD in value
	param		w2		CoordD in value
	param		wstride		Int32 in value
	param		worder		CheckedInt32 in value
	param		points		CoordD in array [COMPSIZE(target/ustride/uorder/vstride/vorder/wstride/worder)]
	dlflags		handcode
	category	SGIX_polynomial_ffd
	version		1.0
	glxflags	SGI ignore
	glxropcode	2073
	extension
	offset		?

DeformationMap3fSGIX(target, u1, u2, ustride, uorder, v1, v2, vstride, vorder, w1, w2, wstride, worder, points)
	return		void
	param		target		FfdTargetSGIX in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	param		ustride		Int32 in value
	param		uorder		CheckedInt32 in value
	param		v1		CoordF in value
	param		v2		CoordF in value
	param		vstride		Int32 in value
	param		vorder		CheckedInt32 in value
	param		w1		CoordF in value
	param		w2		CoordF in value
	param		wstride		Int32 in value
	param		worder		CheckedInt32 in value
	param		points		CoordF in array [COMPSIZE(target/ustride/uorder/vstride/vorder/wstride/worder)]
	category	SGIX_polynomial_ffd
	dlflags		handcode
	version		1.0
	glxflags	SGI ignore
	glxropcode	2074
	extension
	offset		?

DeformSGIX(mask)
	return		void
	param		mask		FfdMaskSGIX in value
	category	SGIX_polynomial_ffd
	version		1.0
	glxflags	SGI ignore
	glxropcode	2075
	extension
	offset		?

LoadIdentityDeformationMapSGIX(mask)
	return		void
	param		mask		FfdMaskSGIX in value
	category	SGIX_polynomial_ffd
	version		1.0
	glxflags	SGI ignore
	glxropcode	2076
	extension
	offset		?

###############################################################################
#
# Extension #60
# SGIX_reference_plane commands
#
###############################################################################

ReferencePlaneSGIX(equation)
	return		void
	param		equation	Float64 in array [4]
	category	SGIX_reference_plane
	version		1.0
	glxflags	SGI
	glxropcode	2071
	extension
	offset		468

###############################################################################
#
# Extension #61
# SGIX_flush_raster commands
#
###############################################################################

FlushRasterSGIX()
	return		void
	category	SGIX_flush_raster
	version		1.0
	dlflags		notlistable
	glxflags	SGI
	glxvendorpriv	4105
	extension
	offset		469

###############################################################################
#
# Extension #62 - GLX_SGIX_cushion
#
###############################################################################

###############################################################################
#
# Extension #63
# SGIX_depth_texture commands
#
###############################################################################

# (none)
newcategory: SGIX_depth_texture

###############################################################################
#
# Extension #64
# SGIS_fog_function commands
#
###############################################################################

FogFuncSGIS(n, points)
	return		void
	param		n		SizeI in value
	param		points		Float32 in array [n*2]
	category	SGIS_fog_function
	version		1.1
	glxflags	SGI
	glxropcode	2067
	extension
	offset

# Need to insert GLX information
GetFogFuncSGIS(points)
	return		void
	param		points		Float32 out array [COMPSIZE()]
	category	SGIS_fog_function
	version		1.1
	dlflags		notlistable
	glxflags	ignore
	extension
	offset

###############################################################################
#
# Extension #65
# SGIX_fog_offset commands
#
###############################################################################

# (none)
newcategory: SGIX_fog_offset

###############################################################################
#
# Extension #66
# HP_image_transform commands
#
###############################################################################

ImageTransformParameteriHP(target, pname, param)
	return		void
	param		target		ImageTransformTargetHP in value
	param		pname		ImageTransformPNameHP in value
	param		param		Int32 in value
	category	HP_image_transform
	version		1.1
	glxropcode	?
	offset		?

ImageTransformParameterfHP(target, pname, param)
	return		void
	param		target		ImageTransformTargetHP in value
	param		pname		ImageTransformPNameHP in value
	param		param		Float32 in value
	category	HP_image_transform
	version		1.1
	glxropcode	?
	offset		?

ImageTransformParameterivHP(target, pname, params)
	return		void
	param		target		ImageTransformTargetHP in value
	param		pname		ImageTransformPNameHP in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	HP_image_transform
	version		1.1
	glxropcode	?
	offset		?

ImageTransformParameterfvHP(target, pname, params)
	return		void
	param		target		ImageTransformTargetHP in value
	param		pname		ImageTransformPNameHP in value
	param		params		Float32 in array [COMPSIZE(pname)]
	category	HP_image_transform
	version		1.1
	glxropcode	?
	offset		?

GetImageTransformParameterivHP(target, pname, params)
	return		void
	param		target		ImageTransformTargetHP in value
	param		pname		ImageTransformPNameHP in value
	param		params		Int32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	HP_image_transform
	version		1.1
	glxropcode	?
	offset		?

GetImageTransformParameterfvHP(target, pname, params)
	return		void
	param		target		ImageTransformTargetHP in value
	param		pname		ImageTransformPNameHP in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	HP_image_transform
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #67
# HP_convolution_border_modes commands
#
###############################################################################

# (none)
newcategory: HP_convolution_border_modes

###############################################################################
#
# Extension #68
# INGR_palette_buffer commands
#
###############################################################################

#@ (Intergraph hasn't provided a spec)

###############################################################################
#
# Extension #69
# SGIX_texture_add_env commands
#
###############################################################################

# (none)
newcategory: SGIX_texture_add_env

###############################################################################
#
# Extension #70 - skipped
# Extension #71 - skipped
# Extension #72 - skipped
# Extension #73 - skipped
#
###############################################################################

###############################################################################
#
# Extension #74
# EXT_color_subtable commands
#
# This was probably never actually shipped as an EXT - just written up as a
# reference for OpenGL 1.2 ARB_imaging.
#
###############################################################################

ColorSubTableEXT(target, start, count, format, type, data)
	return		void
	param		target		ColorTableTarget in value
	param		start		SizeI in value
	param		count		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		data		Void in array [COMPSIZE(format/type/count)]
	category	EXT_color_subtable
	version		1.2
	alias		ColorSubTable

CopyColorSubTableEXT(target, start, x, y, width)
	return		void
	param		target		ColorTableTarget in value
	param		start		SizeI in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	EXT_color_subtable
	version		1.2
	alias		CopyColorSubTable

###############################################################################
#
# Extension #75 - GLU_EXT_object_space_tess
#
###############################################################################

###############################################################################
#
# Extension #76
# PGI_vertex_hints commands
#
###############################################################################

# (none)
newcategory: PGI_vertex_hints

###############################################################################
#
# Extension #77
# PGI_misc_hints commands
#
###############################################################################

HintPGI(target, mode)
	return		void
	param		target		HintTargetPGI in value
	param		mode		Int32 in value
	category	PGI_misc_hints
	version		1.1
	offset		544

###############################################################################
#
# Extension #78
# EXT_paletted_texture commands
#
###############################################################################

ColorTableEXT(target, internalFormat, width, format, type, table)
	return		void
	param		target		ColorTableTarget in value
	param		internalFormat	PixelInternalFormat in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		table		Void in array [COMPSIZE(format/type/width)]
	category	EXT_paletted_texture
	version		1.1
	alias		ColorTable

GetColorTableEXT(target, format, type, data)
	return		void
	param		target		ColorTableTarget in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		data		Void out array [COMPSIZE(target/format/type)]
	category	EXT_paletted_texture
	version		1.1
	offset		550

GetColorTableParameterivEXT(target, pname, params)
	return		void
	param		target		ColorTableTarget in value
	param		pname		GetColorTableParameterPName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_paletted_texture
	version		1.1
	offset		551

GetColorTableParameterfvEXT(target, pname, params)
	return		void
	param		target		ColorTableTarget in value
	param		pname		GetColorTableParameterPName in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_paletted_texture
	version		1.1
	offset		552

###############################################################################
#
# Extension #79
# EXT_clip_volume_hint commands
#
###############################################################################

# (none)
newcategory: EXT_clip_volume_hint

###############################################################################
#
# Extension #80
# SGIX_list_priority commands
#
###############################################################################

# @@@ Needs vendorpriv opcodes assigned
GetListParameterfvSGIX(list, pname, params)
	return		void
	param		list		List in value
	param		pname		ListParameterName in value
	param		params		CheckedFloat32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	glxflags	ignore
	category	SGIX_list_priority
	version		1.0
	glxvendorpriv	?
	extension
	offset		470

# @@@ Needs vendorpriv opcodes assigned
GetListParameterivSGIX(list, pname, params)
	return		void
	param		list		List in value
	param		pname		ListParameterName in value
	param		params		CheckedInt32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	glxflags	ignore
	category	SGIX_list_priority
	version		1.0
	glxvendorpriv	?
	extension
	offset		471

ListParameterfSGIX(list, pname, param)
	return		void
	param		list		List in value
	param		pname		ListParameterName in value
	param		param		CheckedFloat32 in value
	dlflags		notlistable
	glxflags	ignore
	category	SGIX_list_priority
	version		1.0
	glxropcode	2078
	extension
	offset		472

ListParameterfvSGIX(list, pname, params)
	return		void
	param		list		List in value
	param		pname		ListParameterName in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	dlflags		notlistable
	glxflags	ignore
	category	SGIX_list_priority
	version		1.0
	glxropcode	2079
	extension
	offset		473

ListParameteriSGIX(list, pname, param)
	return		void
	param		list		List in value
	param		pname		ListParameterName in value
	param		param		CheckedInt32 in value
	dlflags		notlistable
	glxflags	ignore
	category	SGIX_list_priority
	version		1.0
	glxropcode	2080
	extension
	offset		474

ListParameterivSGIX(list, pname, params)
	return		void
	param		list		List in value
	param		pname		ListParameterName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	dlflags		notlistable
	glxflags	ignore
	category	SGIX_list_priority
	version		1.0
	glxropcode	2081
	extension
	offset		475

###############################################################################
#
# Extension #81
# SGIX_ir_instrument1 commands
#
###############################################################################

# (none)
newcategory: SGIX_ir_instrument1

###############################################################################
#
# Extension #82
# SGIX_calligraphic_fragment commands
#
###############################################################################

# (none)
newcategory: SGIX_calligraphic_fragment

###############################################################################
#
# Extension #83 - GLX_SGIX_video_resize
#
###############################################################################

###############################################################################
#
# Extension #84
# SGIX_texture_lod_bias commands
#
###############################################################################

# (none)
newcategory: SGIX_texture_lod_bias

###############################################################################
#
# Extension #85 - skipped
# Extension #86 - GLX_SGIX_dmbuffer
# Extension #87 - skipped
# Extension #88 - skipped
# Extension #89 - skipped
#
###############################################################################

###############################################################################
#
# Extension #90
# SGIX_shadow_ambient commands
#
###############################################################################

# (none)
newcategory: SGIX_shadow_ambient

###############################################################################
#
# Extension #91 - GLX_SGIX_swap_group
# Extension #92 - GLX_SGIX_swap_barrier
#
###############################################################################

###############################################################################
#
# Extension #93
# EXT_index_texture commands
#
###############################################################################

# (none)
newcategory: EXT_index_texture

###############################################################################
#
# Extension #94
# EXT_index_material commands
#
###############################################################################

IndexMaterialEXT(face, mode)
	return		void
	param		face		MaterialFace in value
	param		mode		IndexMaterialParameterEXT in value
	category	EXT_index_material
	version		1.1
	extension	soft
	glxflags	ignore
	offset		538

###############################################################################
#
# Extension #95
# EXT_index_func commands
#
###############################################################################

IndexFuncEXT(func, ref)
	return		void
	param		func		IndexFunctionEXT in value
	param		ref		ClampedFloat32 in value
	category	EXT_index_func
	version		1.1
	extension	soft
	glxflags	ignore
	offset		539

###############################################################################
#
# Extension #96
# EXT_index_array_formats commands
#
###############################################################################

# (none)
newcategory: EXT_index_array_formats

###############################################################################
#
# Extension #97
# EXT_compiled_vertex_array commands
#
###############################################################################

LockArraysEXT(first, count)
	return		void
	param		first		Int32 in value
	param		count		SizeI in value
	category	EXT_compiled_vertex_array
	version		1.1
	dlflags		notlistable
	extension	soft
	glxflags	ignore
	offset		540

UnlockArraysEXT()
	return		void
	category	EXT_compiled_vertex_array
	version		1.1
	dlflags		notlistable
	extension	soft
	glxflags	ignore
	offset		541

###############################################################################
#
# Extension #98
# EXT_cull_vertex commands
#
###############################################################################

CullParameterdvEXT(pname, params)
	return		void
	param		pname		CullParameterEXT in value
	param		params		Float64 out array [4]
	category	EXT_cull_vertex
	version		1.1
	dlflags		notlistable
	extension	soft
	glxflags	ignore
	offset		542

CullParameterfvEXT(pname, params)
	return		void
	param		pname		CullParameterEXT in value
	param		params		Float32 out array [4]
	category	EXT_cull_vertex
	version		1.1
	dlflags		notlistable
	extension	soft
	glxflags	ignore
	offset		543

###############################################################################
#
# Extension #99 - skipped
# Extension #100 - GLU_EXT_nurbs_tessellator
#
###############################################################################

###############################################################################
#
# Extension #101
# SGIX_ycrcb commands
#
###############################################################################

# (none)
newcategory: SGIX_ycrcb

###############################################################################
#
# Extension #102
# SGIX_fragment_lighting commands
#
###############################################################################

FragmentColorMaterialSGIX(face, mode)
	return		void
	param		face		MaterialFace in value
	param		mode		MaterialParameter in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		476

FragmentLightfSGIX(light, pname, param)
	return		void
	param		light		FragmentLightNameSGIX in value
	param		pname		FragmentLightParameterSGIX in value
	param		param		CheckedFloat32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		477

FragmentLightfvSGIX(light, pname, params)
	return		void
	param		light		FragmentLightNameSGIX in value
	param		pname		FragmentLightParameterSGIX in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		478

FragmentLightiSGIX(light, pname, param)
	return		void
	param		light		FragmentLightNameSGIX in value
	param		pname		FragmentLightParameterSGIX in value
	param		param		CheckedInt32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		479

FragmentLightivSGIX(light, pname, params)
	return		void
	param		light		FragmentLightNameSGIX in value
	param		pname		FragmentLightParameterSGIX in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		480

FragmentLightModelfSGIX(pname, param)
	return		void
	param		pname		FragmentLightModelParameterSGIX in value
	param		param		CheckedFloat32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		481

FragmentLightModelfvSGIX(pname, params)
	return		void
	param		pname		FragmentLightModelParameterSGIX in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		482

FragmentLightModeliSGIX(pname, param)
	return		void
	param		pname		FragmentLightModelParameterSGIX in value
	param		param		CheckedInt32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		483

FragmentLightModelivSGIX(pname, params)
	return		void
	param		pname		FragmentLightModelParameterSGIX in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		484

FragmentMaterialfSGIX(face, pname, param)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		param		CheckedFloat32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		485

FragmentMaterialfvSGIX(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		486

FragmentMaterialiSGIX(face, pname, param)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		param		CheckedInt32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		487

FragmentMaterialivSGIX(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		488

GetFragmentLightfvSGIX(light, pname, params)
	return		void
	param		light		FragmentLightNameSGIX in value
	param		pname		FragmentLightParameterSGIX in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	dlflags		notlistable
	glxflags	ignore
	version		1.0
	extension
	offset		489

GetFragmentLightivSGIX(light, pname, params)
	return		void
	param		light		FragmentLightNameSGIX in value
	param		pname		FragmentLightParameterSGIX in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	dlflags		notlistable
	glxflags	ignore
	version		1.0
	extension
	offset		490

GetFragmentMaterialfvSGIX(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	dlflags		notlistable
	glxflags	ignore
	version		1.0
	extension
	offset		491

GetFragmentMaterialivSGIX(face, pname, params)
	return		void
	param		face		MaterialFace in value
	param		pname		MaterialParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	SGIX_fragment_lighting
	dlflags		notlistable
	glxflags	ignore
	version		1.0
	extension
	offset		492

LightEnviSGIX(pname, param)
	return		void
	param		pname		LightEnvParameterSGIX in value
	param		param		CheckedInt32 in value
	category	SGIX_fragment_lighting
	glxflags	ignore
	version		1.0
	extension
	offset		493

###############################################################################
#
# Extension #103 - skipped
# Extension #104 - skipped
# Extension #105 - skipped
# Extension #106 - skipped
# Extension #107 - skipped
# Extension #108 - skipped
# Extension #109 - skipped
#
###############################################################################

###############################################################################
#
# Extension #110
# IBM_rasterpos_clip commands
#
###############################################################################

# (none)
newcategory: IBM_rasterpos_clip

###############################################################################
#
# Extension #111
# HP_texture_lighting commands
#
###############################################################################

# (none)
newcategory: HP_texture_lighting

###############################################################################
#
# Extension #112
# EXT_draw_range_elements commands
#
###############################################################################

# Spec entries to be written
DrawRangeElementsEXT(mode, start, end, count, type, indices)
	return		void
	param		mode		PrimitiveType in value
	param		start		UInt32 in value
	param		end		UInt32 in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	category	EXT_draw_range_elements
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	alias		DrawRangeElements

###############################################################################
#
# Extension #113
# WIN_phong_shading commands
#
###############################################################################

# (none)
newcategory: WIN_phong_shading

###############################################################################
#
# Extension #114
# WIN_specular_fog commands
#
###############################################################################

# (none)
newcategory: WIN_specular_fog

###############################################################################
#
# Extension #115 - skipped
# Extension #116 - skipped
#
###############################################################################

###############################################################################
#
# Extension #117
# EXT_light_texture commands
#
###############################################################################

# Spec entries to be written
ApplyTextureEXT(mode)
	return		void
	param		mode		LightTextureModeEXT in value
	category	EXT_light_texture
	version		1.1
	glxropcode	?
	offset		?

TextureLightEXT(pname)
	return		void
	param		pname		LightTexturePNameEXT in value
	category	EXT_light_texture
	version		1.1
	glxropcode	?
	offset		?

TextureMaterialEXT(face, mode)
	return		void
	param		face		MaterialFace in value
	param		mode		MaterialParameter in value
	category	EXT_light_texture
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #118 - skipped
#
###############################################################################

###############################################################################
#
# Extension #119
# SGIX_blend_alpha_minmax commands
#
###############################################################################

# (none)
newcategory: SGIX_blend_alpha_minmax

###############################################################################
#
# Extension #120 - skipped
# Extension #121 - skipped
# Extension #122 - skipped
# Extension #123 - skipped
# Extension #124 - skipped
# Extension #125 - skipped
# Extension #126 - skipped
# Extension #127 - skipped
# Extension #128 - skipped
#
###############################################################################

###############################################################################
#
# Extension #129
# EXT_bgra commands
#
###############################################################################

# (none)
newcategory: EXT_bgra

###############################################################################
#
# Extension #130 - skipped
# Extension #131 - skipped
#
###############################################################################

###############################################################################
#
# Extension #132
# SGIX_async commands
#
###############################################################################

AsyncMarkerSGIX(marker)
	return		void
	param		marker		UInt32 in value
	category	SGIX_async
	version		1.0
	glxflags	ignore
	extension
	offset		?

FinishAsyncSGIX(markerp)
	return		Int32
	param		markerp		UInt32 out array [1]
	category	SGIX_async
	version		1.0
	dlflags		notlistable
	glxflags	ignore
	extension
	offset		?

PollAsyncSGIX(markerp)
	return		Int32
	param		markerp		UInt32 out array [1]
	category	SGIX_async
	version		1.0
	dlflags		notlistable
	glxflags	ignore
	extension
	offset		?

GenAsyncMarkersSGIX(range)
	return		UInt32
	param		range		SizeI in value
	category	SGIX_async
	version		1.0
	dlflags		notlistable
	glxflags	ignore
	extension
	offset		?

DeleteAsyncMarkersSGIX(marker, range)
	return		void
	param		marker		UInt32 in value
	param		range		SizeI in value
	category	SGIX_async
	version		1.0
	dlflags		notlistable
	glxflags	ignore
	extension
	offset		?

IsAsyncMarkerSGIX(marker)
	return		Boolean
	param		marker		UInt32 in value
	category	SGIX_async
	version		1.0
	dlflags		notlistable
	glxflags	ignore
	extension
	offset		?

###############################################################################
#
# Extension #133
# SGIX_async_pixel commands
#
###############################################################################

# (none)
newcategory: SGIX_async_pixel

###############################################################################
#
# Extension #134
# SGIX_async_histogram commands
#
###############################################################################

# (none)
newcategory: SGIX_async_histogram

###############################################################################
#
# Extension #135 - skipped (INTEL_texture_scissor was never implemented)
#
###############################################################################

###############################################################################
#
# Extension #136
# INTEL_parallel_arrays commands
#
###############################################################################

VertexPointervINTEL(size, type, pointer)
	return		void
	param		size		Int32 in value
	param		type		VertexPointerType in value
	param		pointer		VoidPointer in array [4] retained
	category	INTEL_parallel_arrays
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.1
	offset		?

NormalPointervINTEL(type, pointer)
	return		void
	param		type		NormalPointerType in value
	param		pointer		VoidPointer in array [4] retained
	category	INTEL_parallel_arrays
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.1
	offset		?

ColorPointervINTEL(size, type, pointer)
	return		void
	param		size		Int32 in value
	param		type		VertexPointerType in value
	param		pointer		VoidPointer in array [4] retained
	category	INTEL_parallel_arrays
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.1
	offset		?

TexCoordPointervINTEL(size, type, pointer)
	return		void
	param		size		Int32 in value
	param		type		VertexPointerType in value
	param		pointer		VoidPointer in array [4] retained
	category	INTEL_parallel_arrays
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.1
	offset		?


###############################################################################
#
# Extension #137
# HP_occlusion_test commands
#
###############################################################################

# (none)
newcategory: HP_occlusion_test

###############################################################################
#
# Extension #138
# EXT_pixel_transform commands
#
###############################################################################

PixelTransformParameteriEXT(target, pname, param)
	return		void
	param		target		PixelTransformTargetEXT in value
	param		pname		PixelTransformPNameEXT in value
	param		param		Int32 in value
	category	EXT_pixel_transform
	version		1.1
	glxropcode	16386
	offset		?

PixelTransformParameterfEXT(target, pname, param)
	return		void
	param		target		PixelTransformTargetEXT in value
	param		pname		PixelTransformPNameEXT in value
	param		param		Float32 in value
	category	EXT_pixel_transform
	version		1.1
	glxropcode	16385
	offset		?

PixelTransformParameterivEXT(target, pname, params)
	return		void
	param		target		PixelTransformTargetEXT in value
	param		pname		PixelTransformPNameEXT in value
	param		params		Int32 in array [1]
	category	EXT_pixel_transform
	version		1.1
	glxropcode	?
	offset		?

PixelTransformParameterfvEXT(target, pname, params)
	return		void
	param		target		PixelTransformTargetEXT in value
	param		pname		PixelTransformPNameEXT in value
	param		params		Float32 in array [1]
	category	EXT_pixel_transform
	version		1.1
	glxropcode	?
	offset		?

GetPixelTransformParameterivEXT(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_pixel_transform
	dlflags		notlistable
	version		1.1
	extension
	glxvendorpriv	2052
	glxflags	ignore
	offset		?

GetPixelTransformParameterfvEXT(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_pixel_transform
	dlflags		notlistable
	version		1.1
	extension
	glxvendorpriv	2051
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #139
# EXT_pixel_transform_color_table commands
#
###############################################################################

# (none)
newcategory: EXT_pixel_transform_color_table

###############################################################################
#
# Extension #140 - skipped
#
###############################################################################

###############################################################################
#
# Extension #141
# EXT_shared_texture_palette commands
#
###############################################################################

# (none)
newcategory: EXT_shared_texture_palette

###############################################################################
#
# Extension #142 - GLX_SGIS_blended_overlay
# Extension #143 - GLX_SGIS_shared_multisample
#
###############################################################################

###############################################################################
#
# Extension #144
# EXT_separate_specular_color commands
#
###############################################################################

# (none)
newcategory: EXT_separate_specular_color

###############################################################################
#
# Extension #145
# EXT_secondary_color commands
#
###############################################################################

SecondaryColor3bEXT(red, green, blue)
	return		void
	param		red		ColorB in value
	param		green		ColorB in value
	param		blue		ColorB in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3bvEXT
	version		1.1
	alias		SecondaryColor3b

SecondaryColor3bvEXT(v)
	return		void
	param		v		ColorB in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4126
	alias		SecondaryColor3bv

SecondaryColor3dEXT(red, green, blue)
	return		void
	param		red		ColorD in value
	param		green		ColorD in value
	param		blue		ColorD in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3dvEXT
	version		1.1
	alias		SecondaryColor3d

SecondaryColor3dvEXT(v)
	return		void
	param		v		ColorD in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4130
	alias		SecondaryColor3dv

SecondaryColor3fEXT(red, green, blue)
	return		void
	param		red		ColorF in value
	param		green		ColorF in value
	param		blue		ColorF in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3fvEXT
	version		1.1
	alias		SecondaryColor3f

SecondaryColor3fvEXT(v)
	return		void
	param		v		ColorF in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4129
	alias		SecondaryColor3fv

SecondaryColor3iEXT(red, green, blue)
	return		void
	param		red		ColorI in value
	param		green		ColorI in value
	param		blue		ColorI in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3ivEXT
	version		1.1
	alias		SecondaryColor3i

SecondaryColor3ivEXT(v)
	return		void
	param		v		ColorI in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4128
	offset		568
	alias		SecondaryColor3iv

SecondaryColor3sEXT(red, green, blue)
	return		void
	param		red		ColorS in value
	param		green		ColorS in value
	param		blue		ColorS in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3svEXT
	version		1.1
	alias		SecondaryColor3s

SecondaryColor3svEXT(v)
	return		void
	param		v		ColorS in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4127
	alias		SecondaryColor3sv

SecondaryColor3ubEXT(red, green, blue)
	return		void
	param		red		ColorUB in value
	param		green		ColorUB in value
	param		blue		ColorUB in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3ubvEXT
	version		1.1
	alias		SecondaryColor3ub

SecondaryColor3ubvEXT(v)
	return		void
	param		v		ColorUB in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4131
	alias		SecondaryColor3ubv

SecondaryColor3uiEXT(red, green, blue)
	return		void
	param		red		ColorUI in value
	param		green		ColorUI in value
	param		blue		ColorUI in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3uivEXT
	version		1.1
	alias		SecondaryColor3ui

SecondaryColor3uivEXT(v)
	return		void
	param		v		ColorUI in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4133
	alias		SecondaryColor3uiv

SecondaryColor3usEXT(red, green, blue)
	return		void
	param		red		ColorUS in value
	param		green		ColorUS in value
	param		blue		ColorUS in value
	category	EXT_secondary_color
	vectorequiv	SecondaryColor3usvEXT
	version		1.1
	alias		SecondaryColor3us

SecondaryColor3usvEXT(v)
	return		void
	param		v		ColorUS in array [3]
	category	EXT_secondary_color
	version		1.1
	glxropcode	4132
	alias		SecondaryColor3usv

SecondaryColorPointerEXT(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		ColorPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	EXT_secondary_color
	dlflags		notlistable
	glxflags	client-handcode server-handcode EXT
	version		1.1
	extension
	alias		SecondaryColorPointer

###############################################################################
#
# Extension #146
# EXT_texture_env commands
#
###############################################################################

# Dead extension - never implemented (removed from registry!)
# (none)
# newcategory: EXT_texture_env

###############################################################################
#
# Extension #147
# EXT_texture_perturb_normal commands
#
###############################################################################

TextureNormalEXT(mode)
	return		void
	param		mode		TextureNormalModeEXT in value
	category	EXT_texture_perturb_normal
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #148
# EXT_multi_draw_arrays commands
#
###############################################################################

# first and count are really 'in'
MultiDrawArraysEXT(mode, first, count, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in array [COMPSIZE(primcount)]
	param		count		SizeI in array [COMPSIZE(primcount)]
	param		primcount	SizeI in value
	category	EXT_multi_draw_arrays
	version		1.1
	glxropcode	?
	alias		MultiDrawArrays

MultiDrawElementsEXT(mode, count, type, indices, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in array [COMPSIZE(primcount)]
	param		type		DrawElementsType in value
	param		indices		VoidPointer in array [COMPSIZE(primcount)]
	param		primcount	SizeI in value
	category	EXT_multi_draw_arrays
	version		1.1
	glxropcode	?
	alias		MultiDrawElements

###############################################################################
#
# Extension #149
# EXT_fog_coord commands
#
###############################################################################

FogCoordfEXT(coord)
	return		void
	param		coord		CoordF in value
	category	EXT_fog_coord
	vectorequiv	FogCoordfvEXT
	version		1.1
	alias		FogCoordf

FogCoordfvEXT(coord)
	return		void
	param		coord		CoordF in array [1]
	category	EXT_fog_coord
	version		1.1
	glxropcode	4124
	alias		FogCoordfv

FogCoorddEXT(coord)
	return		void
	param		coord		CoordD in value
	category	EXT_fog_coord
	vectorequiv	FogCoorddvEXT
	version		1.1
	alias		FogCoordd

FogCoorddvEXT(coord)
	return		void
	param		coord		CoordD in array [1]
	category	EXT_fog_coord
	version		1.1
	glxropcode	4125
	alias		FogCoorddv

FogCoordPointerEXT(type, stride, pointer)
	return		void
	param		type		FogPointerTypeEXT in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	EXT_fog_coord
	dlflags		notlistable
	version		1.1
	glxflags	client-handcode server-handcode EXT
	alias		FogCoordPointer

###############################################################################
#
# Extension #150 - skipped
# Extension #151 - skipped
# Extension #152 - skipped
# Extension #153 - skipped
# Extension #154 - skipped
#
###############################################################################

###############################################################################
#
# Extension #155
# REND_screen_coordinates commands
#
###############################################################################

# (none)
newcategory: REND_screen_coordinates

###############################################################################
#
# Extension #156
# EXT_coordinate_frame commands
#
###############################################################################

Tangent3bEXT(tx, ty, tz)
	return		void
	param		tx		Int8 in value
	param		ty		Int8 in value
	param		tz		Int8 in value
	category	EXT_coordinate_frame
	vectorequiv	Tangent3bvEXT
	version		1.1
	offset		?

Tangent3bvEXT(v)
	return		void
	param		v		Int8 in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Tangent3dEXT(tx, ty, tz)
	return		void
	param		tx		CoordD in value
	param		ty		CoordD in value
	param		tz		CoordD in value
	category	EXT_coordinate_frame
	vectorequiv	Tangent3dvEXT
	version		1.1
	offset		?

Tangent3dvEXT(v)
	return		void
	param		v		CoordD in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Tangent3fEXT(tx, ty, tz)
	return		void
	param		tx		CoordF in value
	param		ty		CoordF in value
	param		tz		CoordF in value
	category	EXT_coordinate_frame
	vectorequiv	Tangent3fvEXT
	version		1.1
	offset		?

Tangent3fvEXT(v)
	return		void
	param		v		CoordF in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Tangent3iEXT(tx, ty, tz)
	return		void
	param		tx		Int32 in value
	param		ty		Int32 in value
	param		tz		Int32 in value
	category	EXT_coordinate_frame
	vectorequiv	Tangent3ivEXT
	version		1.1
	offset		?

Tangent3ivEXT(v)
	return		void
	param		v		Int32 in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Tangent3sEXT(tx, ty, tz)
	return		void
	param		tx		Int16 in value
	param		ty		Int16 in value
	param		tz		Int16 in value
	category	EXT_coordinate_frame
	vectorequiv	Tangent3svEXT
	version		1.1
	offset		?

Tangent3svEXT(v)
	return		void
	param		v		Int16 in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Binormal3bEXT(bx, by, bz)
	return		void
	param		bx		Int8 in value
	param		by		Int8 in value
	param		bz		Int8 in value
	category	EXT_coordinate_frame
	vectorequiv	Binormal3bvEXT
	version		1.1
	offset		?

Binormal3bvEXT(v)
	return		void
	param		v		Int8 in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Binormal3dEXT(bx, by, bz)
	return		void
	param		bx		CoordD in value
	param		by		CoordD in value
	param		bz		CoordD in value
	category	EXT_coordinate_frame
	vectorequiv	Binormal3dvEXT
	version		1.1
	offset		?

Binormal3dvEXT(v)
	return		void
	param		v		CoordD in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Binormal3fEXT(bx, by, bz)
	return		void
	param		bx		CoordF in value
	param		by		CoordF in value
	param		bz		CoordF in value
	category	EXT_coordinate_frame
	vectorequiv	Binormal3fvEXT
	version		1.1
	offset		?

Binormal3fvEXT(v)
	return		void
	param		v		CoordF in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Binormal3iEXT(bx, by, bz)
	return		void
	param		bx		Int32 in value
	param		by		Int32 in value
	param		bz		Int32 in value
	category	EXT_coordinate_frame
	vectorequiv	Binormal3ivEXT
	version		1.1
	offset		?

Binormal3ivEXT(v)
	return		void
	param		v		Int32 in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

Binormal3sEXT(bx, by, bz)
	return		void
	param		bx		Int16 in value
	param		by		Int16 in value
	param		bz		Int16 in value
	category	EXT_coordinate_frame
	vectorequiv	Binormal3svEXT
	version		1.1
	offset		?

Binormal3svEXT(v)
	return		void
	param		v		Int16 in array [3]
	category	EXT_coordinate_frame
	version		1.1
	glxropcode	?
	offset		?

TangentPointerEXT(type, stride, pointer)
	return		void
	param		type		TangentPointerTypeEXT in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	EXT_coordinate_frame
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	offset		?

BinormalPointerEXT(type, stride, pointer)
	return		void
	param		type		BinormalPointerTypeEXT in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	EXT_coordinate_frame
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	offset		?

###############################################################################
#
# Extension #157 - skipped
#
###############################################################################

###############################################################################
#
# Extension #158
# EXT_texture_env_combine commands
#
###############################################################################

# (none)
newcategory: EXT_texture_env_combine

###############################################################################
#
# Extension #159
# APPLE_specular_vector commands
#
###############################################################################

# (none)
newcategory: APPLE_specular_vector

###############################################################################
#
# Extension #160
# APPLE_transform_hint commands
#
###############################################################################

# (none)
newcategory: APPLE_transform_hint

###############################################################################
#
# Extension #161
# SGIX_fog_scale commands
#
###############################################################################

# (none)
newcategory: SGIX_fog_scale

###############################################################################
#
# Extension #162 - skipped
#
###############################################################################

###############################################################################
#
# Extension #163
# SUNX_constant_data commands
#
###############################################################################

FinishTextureSUNX()
	return		void
	category	SUNX_constant_data
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #164
# SUN_global_alpha commands
#
###############################################################################

GlobalAlphaFactorbSUN(factor)
	return		void
	param		factor		Int8 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactorsSUN(factor)
	return		void
	param		factor		Int16 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactoriSUN(factor)
	return		void
	param		factor		Int32 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactorfSUN(factor)
	return		void
	param		factor		Float32 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactordSUN(factor)
	return		void
	param		factor		Float64 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactorubSUN(factor)
	return		void
	param		factor		UInt8 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactorusSUN(factor)
	return		void
	param		factor		UInt16 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

GlobalAlphaFactoruiSUN(factor)
	return		void
	param		factor		UInt32 in value
	category	SUN_global_alpha
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #165
# SUN_triangle_list commands
#
###############################################################################

ReplacementCodeuiSUN(code)
	return		void
	param		code		UInt32 in value
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeusSUN(code)
	return		void
	param		code		UInt16 in value
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeubSUN(code)
	return		void
	param		code		UInt8 in value
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuivSUN(code)
	return		void
	param		code		UInt32 in array [COMPSIZE()]
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeusvSUN(code)
	return		void
	param		code		UInt16 in array [COMPSIZE()]
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeubvSUN(code)
	return		void
	param		code		UInt8 in array [COMPSIZE()]
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodePointerSUN(type, stride, pointer)
	return		void
	param		type		ReplacementCodeTypeSUN in value
	param		stride		SizeI in value
	param		pointer		VoidPointer in array [COMPSIZE(type/stride)] retained
	category	SUN_triangle_list
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #166
# SUN_vertex commands
#
###############################################################################

Color4ubVertex2fSUN(r, g, b, a, x, y)
	return		void
	param		r		UInt8 in value
	param		g		UInt8 in value
	param		b		UInt8 in value
	param		a		UInt8 in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color4ubVertex2fvSUN(c, v)
	return		void
	param		c		UInt8 in array [4]
	param		v		Float32 in array [2]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color4ubVertex3fSUN(r, g, b, a, x, y, z)
	return		void
	param		r		UInt8 in value
	param		g		UInt8 in value
	param		b		UInt8 in value
	param		a		UInt8 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color4ubVertex3fvSUN(c, v)
	return		void
	param		c		UInt8 in array [4]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color3fVertex3fSUN(r, g, b, x, y, z)
	return		void
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color3fVertex3fvSUN(c, v)
	return		void
	param		c		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Normal3fVertex3fSUN(nx, ny, nz, x, y, z)
	return		void
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Normal3fVertex3fvSUN(n, v)
	return		void
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color4fNormal3fVertex3fSUN(r, g, b, a, nx, ny, nz, x, y, z)
	return		void
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		a		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

Color4fNormal3fVertex3fvSUN(c, n, v)
	return		void
	param		c		Float32 in array [4]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fVertex3fSUN(s, t, x, y, z)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fVertex3fvSUN(tc, v)
	return		void
	param		tc		Float32 in array [2]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord4fVertex4fSUN(s, t, p, q, x, y, z, w)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		p		Float32 in value
	param		q		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord4fVertex4fvSUN(tc, v)
	return		void
	param		tc		Float32 in array [4]
	param		v		Float32 in array [4]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fColor4ubVertex3fSUN(s, t, r, g, b, a, x, y, z)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		r		UInt8 in value
	param		g		UInt8 in value
	param		b		UInt8 in value
	param		a		UInt8 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fColor4ubVertex3fvSUN(tc, c, v)
	return		void
	param		tc		Float32 in array [2]
	param		c		UInt8 in array [4]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fColor3fVertex3fSUN(s, t, r, g, b, x, y, z)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fColor3fVertex3fvSUN(tc, c, v)
	return		void
	param		tc		Float32 in array [2]
	param		c		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fNormal3fVertex3fSUN(s, t, nx, ny, nz, x, y, z)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fNormal3fVertex3fvSUN(tc, n, v)
	return		void
	param		tc		Float32 in array [2]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fColor4fNormal3fVertex3fSUN(s, t, r, g, b, a, nx, ny, nz, x, y, z)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		a		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord2fColor4fNormal3fVertex3fvSUN(tc, c, n, v)
	return		void
	param		tc		Float32 in array [2]
	param		c		Float32 in array [4]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord4fColor4fNormal3fVertex4fSUN(s, t, p, q, r, g, b, a, nx, ny, nz, x, y, z, w)
	return		void
	param		s		Float32 in value
	param		t		Float32 in value
	param		p		Float32 in value
	param		q		Float32 in value
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		a		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

TexCoord4fColor4fNormal3fVertex4fvSUN(tc, c, n, v)
	return		void
	param		tc		Float32 in array [4]
	param		c		Float32 in array [4]
	param		n		Float32 in array [3]
	param		v		Float32 in array [4]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiVertex3fSUN(rc, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiVertex3fvSUN(rc, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiColor4ubVertex3fSUN(rc, r, g, b, a, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		r		UInt8 in value
	param		g		UInt8 in value
	param		b		UInt8 in value
	param		a		UInt8 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiColor4ubVertex3fvSUN(rc, c, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		c		UInt8 in array [4]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiColor3fVertex3fSUN(rc, r, g, b, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiColor3fVertex3fvSUN(rc, c, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		c		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiNormal3fVertex3fSUN(rc, nx, ny, nz, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiNormal3fVertex3fvSUN(rc, n, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiColor4fNormal3fVertex3fSUN(rc, r, g, b, a, nx, ny, nz, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		a		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiColor4fNormal3fVertex3fvSUN(rc, c, n, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		c		Float32 in array [4]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiTexCoord2fVertex3fSUN(rc, s, t, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		s		Float32 in value
	param		t		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiTexCoord2fVertex3fvSUN(rc, tc, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		tc		Float32 in array [2]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiTexCoord2fNormal3fVertex3fSUN(rc, s, t, nx, ny, nz, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		s		Float32 in value
	param		t		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiTexCoord2fNormal3fVertex3fvSUN(rc, tc, n, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		tc		Float32 in array [2]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiTexCoord2fColor4fNormal3fVertex3fSUN(rc, s, t, r, g, b, a, nx, ny, nz, x, y, z)
	return		void
	param		rc		ReplacementCodeSUN in value
	param		s		Float32 in value
	param		t		Float32 in value
	param		r		Float32 in value
	param		g		Float32 in value
	param		b		Float32 in value
	param		a		Float32 in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

ReplacementCodeuiTexCoord2fColor4fNormal3fVertex3fvSUN(rc, tc, c, n, v)
	return		void
	param		rc		ReplacementCodeSUN in array [1]
	param		tc		Float32 in array [2]
	param		c		Float32 in array [4]
	param		n		Float32 in array [3]
	param		v		Float32 in array [3]
	category	SUN_vertex
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #167 - WGL_EXT_display_color_table
# Extension #168 - WGL_EXT_extensions_string
# Extension #169 - WGL_EXT_make_current_read
# Extension #170 - WGL_EXT_pixel_format
# Extension #171 - WGL_EXT_pbuffer
# Extension #172 - WGL_EXT_swap_control
#
###############################################################################

###############################################################################
#
# Extension #173
# EXT_blend_func_separate commands (also INGR_blend_func_separate)
#
###############################################################################

BlendFuncSeparateEXT(sfactorRGB, dfactorRGB, sfactorAlpha, dfactorAlpha)
	return		void
	param		sfactorRGB	BlendFuncSeparateParameterEXT in value
	param		dfactorRGB	BlendFuncSeparateParameterEXT in value
	param		sfactorAlpha	BlendFuncSeparateParameterEXT in value
	param		dfactorAlpha	BlendFuncSeparateParameterEXT in value
	category	EXT_blend_func_separate
	glxropcode	4134
	version		1.0
	extension
	alias		BlendFuncSeparate

BlendFuncSeparateINGR(sfactorRGB, dfactorRGB, sfactorAlpha, dfactorAlpha)
	return		void
	param		sfactorRGB	BlendFuncSeparateParameterEXT in value
	param		dfactorRGB	BlendFuncSeparateParameterEXT in value
	param		sfactorAlpha	BlendFuncSeparateParameterEXT in value
	param		dfactorAlpha	BlendFuncSeparateParameterEXT in value
	category	INGR_blend_func_separate
	glxropcode	4134
	version		1.0
	extension
	alias		BlendFuncSeparateEXT

###############################################################################
#
# Extension #174
# INGR_color_clamp commands
#
###############################################################################

# (none)
newcategory: INGR_color_clamp

###############################################################################
#
# Extension #175
# INGR_interlace_read commands
#
###############################################################################

# (none)
newcategory: INGR_interlace_read

###############################################################################
#
# Extension #176
# EXT_stencil_wrap commands
#
###############################################################################

# (none)
newcategory: EXT_stencil_wrap

###############################################################################
#
# Extension #177 - skipped
#
###############################################################################

###############################################################################
#
# Extension #178
# EXT_422_pixels commands
#
###############################################################################

# (none)
newcategory: EXT_422_pixels

###############################################################################
#
# Extension #179
# NV_texgen_reflection commands
#
###############################################################################

# (none)
newcategory: NV_texgen_reflection

###############################################################################
#
# Extension #180 - skipped
# Extension #181 - skipped
#
###############################################################################

###############################################################################
#
# Extension #182
# SUN_convolution_border_modes commands
#
###############################################################################

# (none)
newcategory: SUN_convolution_border_modes

###############################################################################
#
# Extension #183 - GLX_SUN_get_transparent_index
# Extension #184 - skipped
#
###############################################################################

###############################################################################
#
# Extension #185
# EXT_texture_env_add commands
#
###############################################################################

# (none)
newcategory: EXT_texture_env_add

###############################################################################
#
# Extension #186
# EXT_texture_lod_bias commands
#
###############################################################################

# (none)
newcategory: EXT_texture_lod_bias

###############################################################################
#
# Extension #187
# EXT_texture_filter_anisotropic commands
#
###############################################################################

# (none)
newcategory: EXT_texture_filter_anisotropic

###############################################################################
#
# Extension #188
# EXT_vertex_weighting commands
#
###############################################################################

# GLX stuff to be written
VertexWeightfEXT(weight)
	return		void
	param		weight		Float32 in value
	category	EXT_vertex_weighting
	vectorequiv	VertexWeightfvEXT
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		494

VertexWeightfvEXT(weight)
	return		void
	param		weight		Float32 in array [1]
	category	EXT_vertex_weighting
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4135
	glxflags	ignore
	offset		495

VertexWeightPointerEXT(size, type, stride, pointer)
	return		void
	param		size		Int32 in value
	param		type		VertexWeightPointerTypeEXT in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(type/stride)] retained
	category	EXT_vertex_weighting
	version		1.1
	extension	soft WINSOFT NV10
	dlflags		notlistable
	glxflags	ignore
	offset		496

###############################################################################
#
# Extension #189
# NV_light_max_exponent commands
#
###############################################################################

# (none)
newcategory: NV_light_max_exponent

###############################################################################
#
# Extension #190
# NV_vertex_array_range commands
#
###############################################################################

FlushVertexArrayRangeNV()
	return		void
	category	NV_vertex_array_range
	version		1.1
	extension	soft WINSOFT NV10
	dlflags		notlistable
	glxflags	client-handcode server-handcode ignore
	offset		497

VertexArrayRangeNV(length, pointer)
	return		void
	param		length		SizeI in value
	param		pointer		Void in array [COMPSIZE(length)] retained
	category	NV_vertex_array_range
	version		1.1
	extension	soft WINSOFT NV10
	dlflags		notlistable
	glxflags	client-handcode server-handcode ignore
	offset		498

###############################################################################
#
# Extension #191
# NV_register_combiners commands
#
###############################################################################

CombinerParameterfvNV(pname, params)
	return		void
	param		pname		CombinerParameterNV in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4137
	glxflags	ignore
	offset		499

CombinerParameterfNV(pname, param)
	return		void
	param		pname		CombinerParameterNV in value
	param		param		Float32 in value
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4136
	glxflags	ignore
	offset		500

CombinerParameterivNV(pname, params)
	return		void
	param		pname		CombinerParameterNV in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4139
	glxflags	ignore
	offset		501

CombinerParameteriNV(pname, param)
	return		void
	param		pname		CombinerParameterNV in value
	param		param		Int32 in value
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4138
	glxflags	ignore
	offset		502

CombinerInputNV(stage, portion, variable, input, mapping, componentUsage)
	return		void
	param		stage		CombinerStageNV in value
	param		portion		CombinerPortionNV in value
	param		variable	CombinerVariableNV in value
	param		input		CombinerRegisterNV in value
	param		mapping		CombinerMappingNV in value
	param		componentUsage	CombinerComponentUsageNV in value
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4140
	glxflags	ignore
	offset		503

CombinerOutputNV(stage, portion, abOutput, cdOutput, sumOutput, scale, bias, abDotProduct, cdDotProduct, muxSum)
	return		void
	param		stage		CombinerStageNV in value
	param		portion		CombinerPortionNV in value
	param		abOutput	CombinerRegisterNV in value
	param		cdOutput	CombinerRegisterNV in value
	param		sumOutput	CombinerRegisterNV in value
	param		scale		CombinerScaleNV in value
	param		bias		CombinerBiasNV in value
	param		abDotProduct	Boolean in value
	param		cdDotProduct	Boolean in value
	param		muxSum		Boolean in value
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4141
	glxflags	ignore
	offset		504

FinalCombinerInputNV(variable, input, mapping, componentUsage)
	return		void
	param		variable	CombinerVariableNV in value
	param		input		CombinerRegisterNV in value
	param		mapping		CombinerMappingNV in value
	param		componentUsage	CombinerComponentUsageNV in value
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxropcode	4142
	glxflags	ignore
	offset		505

GetCombinerInputParameterfvNV(stage, portion, variable, pname, params)
	return		void
	param		stage		CombinerStageNV in value
	param		portion		CombinerPortionNV in value
	param		variable	CombinerVariableNV in value
	param		pname		CombinerParameterNV in value
	param		params		Float32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxvendorpriv	1270
	glxflags	ignore
	offset		506

GetCombinerInputParameterivNV(stage, portion, variable, pname, params)
	return		void
	param		stage		CombinerStageNV in value
	param		portion		CombinerPortionNV in value
	param		variable	CombinerVariableNV in value
	param		pname		CombinerParameterNV in value
	param		params		Int32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxvendorpriv	1271
	glxflags	ignore
	offset		507

GetCombinerOutputParameterfvNV(stage, portion, pname, params)
	return		void
	param		stage		CombinerStageNV in value
	param		portion		CombinerPortionNV in value
	param		pname		CombinerParameterNV in value
	param		params		Float32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxvendorpriv	1272
	glxflags	ignore
	offset		508

GetCombinerOutputParameterivNV(stage, portion, pname, params)
	return		void
	param		stage		CombinerStageNV in value
	param		portion		CombinerPortionNV in value
	param		pname		CombinerParameterNV in value
	param		params		Int32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxvendorpriv	1273
	glxflags	ignore
	offset		509

GetFinalCombinerInputParameterfvNV(variable, pname, params)
	return		void
	param		variable	CombinerVariableNV in value
	param		pname		CombinerParameterNV in value
	param		params		Float32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxvendorpriv	1274
	glxflags	ignore
	offset		510

GetFinalCombinerInputParameterivNV(variable, pname, params)
	return		void
	param		variable	CombinerVariableNV in value
	param		pname		CombinerParameterNV in value
	param		params		Int32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners
	version		1.1
	extension	soft WINSOFT NV10
	glxvendorpriv	1275
	glxflags	ignore
	offset		511

###############################################################################
#
# Extension #192
# NV_fog_distance commands
#
###############################################################################

# (none)
newcategory: NV_fog_distance

###############################################################################
#
# Extension #193
# NV_texgen_emboss commands
#
###############################################################################

# (none)
newcategory: NV_texgen_emboss

###############################################################################
#
# Extension #194
# NV_blend_square commands
#
###############################################################################

# (none)
newcategory: NV_blend_square

###############################################################################
#
# Extension #195
# NV_texture_env_combine4 commands
#
###############################################################################

# (none)
newcategory: NV_texture_env_combine4

###############################################################################
#
# Extension #196
# MESA_resize_buffers commands
#
###############################################################################

ResizeBuffersMESA()
	return		void
	category	MESA_resize_buffers
	version		1.0
	glxropcode	?
	offset		512

###############################################################################
#
# Extension #197
# MESA_window_pos commands
#
# Note that the 2- and 3-component versions are now aliases of ARB
# entry points.
#
###############################################################################

WindowPos2dMESA(x, y)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	category	MESA_window_pos
	vectorequiv	WindowPos2dvMESA
	version		1.0
	alias		WindowPos2dARB

WindowPos2dvMESA(v)
	return		void
	param		v		CoordD in array [2]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos2dvARB

WindowPos2fMESA(x, y)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	category	MESA_window_pos
	vectorequiv	WindowPos2fvMESA
	version		1.0
	alias		WindowPos2fARB

WindowPos2fvMESA(v)
	return		void
	param		v		CoordF in array [2]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos2fvARB

WindowPos2iMESA(x, y)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	category	MESA_window_pos
	vectorequiv	WindowPos2ivMESA
	version		1.0
	alias		WindowPos2iARB

WindowPos2ivMESA(v)
	return		void
	param		v		CoordI in array [2]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos2ivARB

WindowPos2sMESA(x, y)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	category	MESA_window_pos
	vectorequiv	WindowPos2svMESA
	version		1.0
	alias		WindowPos2sARB

WindowPos2svMESA(v)
	return		void
	param		v		CoordS in array [2]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos2svARB

WindowPos3dMESA(x, y, z)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	vectorequiv	WindowPos3dvMESA
	category	MESA_window_pos
	version		1.0
	alias		WindowPos3dARB

WindowPos3dvMESA(v)
	return		void
	param		v		CoordD in array [3]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos3dvARB

WindowPos3fMESA(x, y, z)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	category	MESA_window_pos
	vectorequiv	WindowPos3fvMESA
	version		1.0
	alias		WindowPos3fARB

WindowPos3fvMESA(v)
	return		void
	param		v		CoordF in array [3]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos3fvARB

WindowPos3iMESA(x, y, z)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	category	MESA_window_pos
	vectorequiv	WindowPos3ivMESA
	version		1.0
	alias		WindowPos3iARB

WindowPos3ivMESA(v)
	return		void
	param		v		CoordI in array [3]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos3ivARB

WindowPos3sMESA(x, y, z)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	category	MESA_window_pos
	vectorequiv	WindowPos3svMESA
	version		1.0
	alias		WindowPos3sARB

WindowPos3svMESA(v)
	return		void
	param		v		CoordS in array [3]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	alias		WindowPos3svARB

WindowPos4dMESA(x, y, z, w)
	return		void
	param		x		CoordD in value
	param		y		CoordD in value
	param		z		CoordD in value
	param		w		CoordD in value
	vectorequiv	WindowPos4dvMESA
	category	MESA_window_pos
	version		1.0
	offset		529

WindowPos4dvMESA(v)
	return		void
	param		v		CoordD in array [4]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	offset		530

WindowPos4fMESA(x, y, z, w)
	return		void
	param		x		CoordF in value
	param		y		CoordF in value
	param		z		CoordF in value
	param		w		CoordF in value
	category	MESA_window_pos
	vectorequiv	WindowPos4fvMESA
	version		1.0
	offset		531

WindowPos4fvMESA(v)
	return		void
	param		v		CoordF in array [4]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	offset		532

WindowPos4iMESA(x, y, z, w)
	return		void
	param		x		CoordI in value
	param		y		CoordI in value
	param		z		CoordI in value
	param		w		CoordI in value
	category	MESA_window_pos
	vectorequiv	WindowPos4ivMESA
	version		1.0
	offset		533

WindowPos4ivMESA(v)
	return		void
	param		v		CoordI in array [4]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	offset		534

WindowPos4sMESA(x, y, z, w)
	return		void
	param		x		CoordS in value
	param		y		CoordS in value
	param		z		CoordS in value
	param		w		CoordS in value
	category	MESA_window_pos
	vectorequiv	WindowPos4svMESA
	version		1.0
	offset		535

WindowPos4svMESA(v)
	return		void
	param		v		CoordS in array [4]
	category	MESA_window_pos
	version		1.0
	glxropcode	?
	offset		536

###############################################################################
#
# Extension #198
# EXT_texture_compression_s3tc commands
#
###############################################################################

newcategory: EXT_texture_compression_s3tc

###############################################################################
#
# Extension #199
# IBM_cull_vertex commands
#
###############################################################################

# (none)
newcategory: IBM_cull_vertex

###############################################################################
#
# Extension #200
# IBM_multimode_draw_arrays commands
#
###############################################################################

MultiModeDrawArraysIBM(mode, first, count, primcount, modestride)
	return		void
	param		mode		PrimitiveType in array [COMPSIZE(primcount)]
	param		first		Int32 in array [COMPSIZE(primcount)]
	param		count		SizeI in array [COMPSIZE(primcount)]
	param		primcount	SizeI in value
	param		modestride	Int32 in value
	category	IBM_multimode_draw_arrays
	version		1.1
	glxropcode	?
	offset		708


MultiModeDrawElementsIBM(mode, count, type, indices, primcount, modestride)
	return		void
	param		mode		PrimitiveType in array [COMPSIZE(primcount)]
	param		count		SizeI in array [COMPSIZE(primcount)]
	param		type		DrawElementsType in value
	param		indices		ConstVoidPointer in array [COMPSIZE(primcount)]
	param		primcount	SizeI in value
	param		modestride	Int32 in value
	category	IBM_multimode_draw_arrays
	version		1.1
	glxropcode	?
	offset		709

###############################################################################
#
# Extension #201
# IBM_vertex_array_lists commands
#
###############################################################################

ColorPointerListIBM(size, type, stride, pointer, ptrstride)
	return		void
	param		size		Int32 in value
	param		type		ColorPointerType in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(size/type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

SecondaryColorPointerListIBM(size, type, stride, pointer, ptrstride)
	return		void
	param		size		Int32 in value
	param		type		SecondaryColorPointerTypeIBM in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(size/type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

EdgeFlagPointerListIBM(stride, pointer, ptrstride)
	return		void
	param		stride		Int32 in value
	param		pointer		BooleanPointer in array [COMPSIZE(stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

FogCoordPointerListIBM(type, stride, pointer, ptrstride)
	return		void
	param		type		FogPointerTypeIBM in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

IndexPointerListIBM(type, stride, pointer, ptrstride)
	return		void
	param		type		IndexPointerType in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

NormalPointerListIBM(type, stride, pointer, ptrstride)
	return		void
	param		type		NormalPointerType in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

TexCoordPointerListIBM(size, type, stride, pointer, ptrstride)
	return		void
	param		size		Int32 in value
	param		type		TexCoordPointerType in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(size/type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

VertexPointerListIBM(size, type, stride, pointer, ptrstride)
	return		void
	param		size		Int32 in value
	param		type		VertexPointerType in value
	param		stride		Int32 in value
	param		pointer		VoidPointer in array [COMPSIZE(size/type/stride)] retained
	param		ptrstride	Int32 in value
	category	IBM_vertex_array_lists
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #202
# SGIX_subsample commands
#
###############################################################################

# (none)
newcategory: SGIX_subsample

###############################################################################
#
# Extension #203
# SGIX_ycrcba commands
#
###############################################################################

# (none)
newcategory: SGIX_ycrcba

###############################################################################
#
# Extension #204
# SGIX_ycrcb_subsample commands
#
###############################################################################

# (none)
newcategory: SGIX_ycrcb_subsample

###############################################################################
#
# Extension #205
# SGIX_depth_pass_instrument commands
#
###############################################################################

# (none)
newcategory: SGIX_depth_pass_instrument

###############################################################################
#
# Extension #206
# 3DFX_texture_compression_FXT1 commands
#
###############################################################################

# (none)
newcategory: 3DFX_texture_compression_FXT1

###############################################################################
#
# Extension #207
# 3DFX_multisample commands
#
###############################################################################

# (none)
newcategory: 3DFX_multisample

###############################################################################
#
# Extension #208
# 3DFX_tbuffer commands
#
###############################################################################

TbufferMask3DFX(mask)
	return		void
	param		mask		UInt32 in value
	category	3DFX_tbuffer
	version		1.2
	glxropcode	?
	offset		553

###############################################################################
#
# Extension #209
# EXT_multisample commands
#
###############################################################################

SampleMaskEXT(value, invert)
	return		void
	param		value		ClampedFloat32 in value
	param		invert		Boolean in value
	category	EXT_multisample
	version		1.0
	glxropcode	?
	extension
	offset		446

SamplePatternEXT(pattern)
	return		void
	param		pattern		SamplePatternEXT in value
	category	EXT_multisample
	version		1.0
	glxropcode	?
	glxflags
	extension
	offset		447

###############################################################################
#
# Extension #210
# SGIX_vertex_preclip commands
#
###############################################################################

# (none)
newcategory: SGIX_vertex_preclip

###############################################################################
#
# Extension #211
# SGIX_convolution_accuracy commands
#
###############################################################################

# (none)
newcategory: SGIX_convolution_accuracy

###############################################################################
#
# Extension #212
# SGIX_resample commands
#
###############################################################################

# (none)
newcategory: SGIX_resample

###############################################################################
#
# Extension #213
# SGIS_point_line_texgen commands
#
###############################################################################

# (none)
newcategory: SGIS_point_line_texgen

###############################################################################
#
# Extension #214
# SGIS_texture_color_mask commands
#
###############################################################################

TextureColorMaskSGIS(red, green, blue, alpha)
	return		void
	param		red		Boolean in value
	param		green		Boolean in value
	param		blue		Boolean in value
	param		alpha		Boolean in value
	category	SGIS_texture_color_mask
	version		1.1
	glxropcode	2082
	extension
	offset		?

###############################################################################
#
# Extension #215 - GLX_MESA_copy_sub_buffer
# Extension #216 - GLX_MESA_pixmap_colormap
# Extension #217 - GLX_MESA_release_buffers
# Extension #218 - GLX_MESA_set_3dfx_mode
#
###############################################################################

###############################################################################
#
# Extension #219
# SGIX_igloo_interface commands
#
###############################################################################

IglooInterfaceSGIX(pname, params)
	return		void
	dlflags		notlistable
	param		pname		IglooFunctionSelectSGIX in value
	param		params		IglooParameterSGIX in array [COMPSIZE(pname)]
	category	SGIX_igloo_interface
	version		1.0
	glxflags	SGI ignore
	extension
	glxropcode	200
	offset		?

###############################################################################
#
# Extension #220
# EXT_texture_env_dot3 commands
#
###############################################################################

# (none)
newcategory: EXT_texture_env_dot3

###############################################################################
#
# Extension #221
# ATI_texture_mirror_once commands
#
###############################################################################
# (none)
newcategory: ATI_texture_mirror_once

###############################################################################
#
# Extension #222
# NV_fence commands
#
###############################################################################

DeleteFencesNV(n, fences)
	return		void
	param		n		SizeI in value
	param		fences		FenceNV in array [n]
	category	NV_fence
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1276
	glxflags	ignore
	offset		647

GenFencesNV(n, fences)
	return		void
	param		n		SizeI in value
	param		fences		FenceNV out array [n]
	category	NV_fence
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1277
	glxflags	ignore
	offset		648

IsFenceNV(fence)
	return		Boolean
	param		fence		FenceNV in value
	category	NV_fence
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1278
	glxflags	ignore
	offset		649

TestFenceNV(fence)
	return		Boolean
	param		fence		FenceNV in value
	category	NV_fence
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1279
	glxflags	ignore
	offset		650

GetFenceivNV(fence, pname, params)
	return		void
	param		fence		FenceNV in value
	param		pname		FenceParameterNameNV in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	NV_fence
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1280
	glxflags	ignore
	offset		651

FinishFenceNV(fence)
	return		void
	param		fence		FenceNV in value
	category	NV_fence
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1312
	glxflags	ignore
	offset		652

SetFenceNV(fence, condition)
	return		void
	param		fence		FenceNV in value
	param		condition	FenceConditionNV in value
	category	NV_fence
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		653

###############################################################################
#
# Extension #223
# IBM_static_data commands
#
###############################################################################

FlushStaticDataIBM(target)
	return		void
	param		target		GLenum in value
	category	IBM_static_data
	version		1.0
	glxflags	ignore

###############################################################################
#
# Extension #224
# IBM_texture_mirrored_repeat commands
#
###############################################################################
# (none)
newcategory: IBM_texture_mirrored_repeat

###############################################################################
#
# Extension #225
# NV_evaluators commands
#
###############################################################################

MapControlPointsNV(target, index, type, ustride, vstride, uorder, vorder, packed, points)
	return		void
	param		target		EvalTargetNV in value
	param		index		UInt32 in value
	param		type		MapTypeNV in value
	param		ustride		SizeI in value
	param		vstride		SizeI in value
	param		uorder		CheckedInt32 in value
	param		vorder		CheckedInt32 in value
	param		packed		Boolean in value
	param		points		Void in array [COMPSIZE(target/uorder/vorder)]
	category	NV_evaluators
	dlflags		handcode
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

MapParameterivNV(target, pname, params)
	return		void
	param		target		EvalTargetNV in value
	param		pname		MapParameterNV in value
	param		params		CheckedInt32 in array [COMPSIZE(target/pname)]
	category	NV_evaluators
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

MapParameterfvNV(target, pname, params)
	return		void
	param		target		EvalTargetNV in value
	param		pname		MapParameterNV in value
	param		params		CheckedFloat32 in array [COMPSIZE(target/pname)]
	category	NV_evaluators
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

GetMapControlPointsNV(target, index, type, ustride, vstride, packed, points)
	return		void
	param		target		EvalTargetNV in value
	param		index		UInt32 in value
	param		type		MapTypeNV in value
	param		ustride		SizeI in value
	param		vstride		SizeI in value
	param		packed		Boolean in value
	param		points		Void out array [COMPSIZE(target)]
	category	NV_evaluators
	dlflags		notlistable
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

GetMapParameterivNV(target, pname, params)
	return		void
	param		target		EvalTargetNV in value
	param		pname		MapParameterNV in value
	param		params		Int32 out array [COMPSIZE(target/pname)]
	category	NV_evaluators
	dlflags		notlistable
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

GetMapParameterfvNV(target, pname, params)
	return		void
	param		target		EvalTargetNV in value
	param		pname		MapParameterNV in value
	param		params		Float32 out array [COMPSIZE(target/pname)]
	category	NV_evaluators
	dlflags		notlistable
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

GetMapAttribParameterivNV(target, index, pname, params)
	return		void
	param		target		EvalTargetNV in value
	param		index		UInt32 in value
	param		pname		MapAttribParameterNV in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	NV_evaluators
	dlflags		notlistable
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

GetMapAttribParameterfvNV(target, index, pname, params)
	return		void
	param		target		EvalTargetNV in value
	param		index		UInt32 in value
	param		pname		MapAttribParameterNV in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	NV_evaluators
	dlflags		notlistable
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

EvalMapsNV(target, mode)
	return		void
	param		target		EvalTargetNV in value
	param		mode		EvalMapsModeNV in value
	category	NV_evaluators
	version		1.1
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #226
# NV_packed_depth_stencil commands
#
###############################################################################

# (none)
newcategory: NV_packed_depth_stencil

###############################################################################
#
# Extension #227
# NV_register_combiners2 commands
#
###############################################################################

CombinerStageParameterfvNV(stage, pname, params)
	return		void
	param		stage		CombinerStageNV in value
	param		pname		CombinerParameterNV in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	NV_register_combiners2
	version		1.1
	extension
	glxflags	ignore
	offset		?

GetCombinerStageParameterfvNV(stage, pname, params)
	return		void
	param		stage		CombinerStageNV in value
	param		pname		CombinerParameterNV in value
	param		params		Float32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_register_combiners2
	version		1.1
	extension
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #228
# NV_texture_compression_vtc commands
#
###############################################################################

# (none)
newcategory: NV_texture_compression_vtc

###############################################################################
#
# Extension #229
# NV_texture_rectangle commands
#
###############################################################################

# (none)
newcategory: NV_texture_rectangle

###############################################################################
#
# Extension #230
# NV_texture_shader commands
#
###############################################################################

# (none)
newcategory: NV_texture_shader

###############################################################################
#
# Extension #231
# NV_texture_shader2 commands
#
###############################################################################

# (none)
newcategory: NV_texture_shader2

###############################################################################
#
# Extension #232
# NV_vertex_array_range2 commands
#
###############################################################################

# (none)
newcategory: NV_vertex_array_range2

###############################################################################
#
# Extension #233
# NV_vertex_program commands
#
###############################################################################

AreProgramsResidentNV(n, programs, residences)
	return		Boolean
	param		n		SizeI in value
	param		programs	UInt32 in array [n]
	param		residences	Boolean out array [n]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxvendorpriv	1293
	offset		578

BindProgramNV(target, id)
	return		void
	param		target		VertexAttribEnumNV in value
	param		id		UInt32 in value
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4180
	alias		BindProgramARB

DeleteProgramsNV(n, programs)
	return		void
	param		n		SizeI in value
	param		programs	UInt32 in array [n]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1294
	alias		DeleteProgramsARB

ExecuteProgramNV(target, id, params)
	return		void
	param		target		VertexAttribEnumNV in value
	param		id		UInt32 in value
	param		params		Float32 in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxropcode	4181
	offset		581

GenProgramsNV(n, programs)
	return		void
	param		n		SizeI in value
	param		programs	UInt32 out array [n]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1295
	alias		GenProgramsARB

GetProgramParameterdvNV(target, index, pname, params)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Float64 out array [4]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxvendorpriv	1297
	offset		583

GetProgramParameterfvNV(target, index, pname, params)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Float32 out array [4]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxvendorpriv	1296
	offset		584

# GetProgramParameterSigneddvNV(target, index, pname, params)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  pname		  VertexAttribEnumNV in value
#	  param		  params	  Float64 out array [4]
#	  category	  NV_vertex_program1_1_dcc
#	  dlflags	  notlistable
#	  version	  1.2
#	  extension	  soft WINSOFT NV20
#	  glxflags	  ignore
#	  offset	  ?
#
# GetProgramParameterSignedfvNV(target, index, pname, params)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  pname		  VertexAttribEnumNV in value
#	  param		  params	  Float32 out array [4]
#	  category	  NV_vertex_program1_1_dcc
#	  dlflags	  notlistable
#	  version	  1.2
#	  extension	  soft WINSOFT NV20
#	  glxflags	  ignore
#	  offset	  ?

GetProgramivNV(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Int32 out array [4]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxvendorpriv	1298
	offset		585

GetProgramStringNV(id, pname, program)
	return		void
	param		id		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		program		ProgramCharacterNV out array [COMPSIZE(id/pname)]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxvendorpriv	1299
	offset		586

GetTrackMatrixivNV(target, address, pname, params)
	return		void
	param		target		VertexAttribEnumNV in value
	param		address		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Int32 out array [1]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	glxvendorpriv	1300
	offset		587

GetVertexAttribdvNV(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Float64 out array [1]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1301
	alias		GetVertexAttribdv

GetVertexAttribfvNV(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Float32 out array [1]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1302
	alias		GetVertexAttribfv

GetVertexAttribivNV(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		params		Int32 out array [1]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1303
	alias		GetVertexAttribiv

GetVertexAttribPointervNV(index, pname, pointer)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnumNV in value
	param		pointer		VoidPointer out array [1]
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	alias		GetVertexAttribPointerv

IsProgramNV(id)
	return		Boolean
	param		id		UInt32 in value
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxvendorpriv	1304
	alias		IsProgram

LoadProgramNV(target, id, len, program)
	return		void
	param		target		VertexAttribEnumNV in value
	param		id		UInt32 in value
	param		len		SizeI in value
	param		program		UInt8 in array [len]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4183
	offset		593

ProgramParameter4dNV(target, index, x, y, z, w)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	ProgramParameter4dvNV
	extension	soft WINSOFT NV10
	offset		594

ProgramParameter4dvNV(target, index, v)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		v		Float64 in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4185
	offset		595

ProgramParameter4fNV(target, index, x, y, z, w)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	ProgramParameter4fvNV
	extension	soft WINSOFT NV10
	offset		596

ProgramParameter4fvNV(target, index, v)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		v		Float32 in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4184
	offset		597

ProgramParameters4dvNV(target, index, count, v)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float64 in array [count*4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4187
	offset		598

ProgramParameters4fvNV(target, index, count, v)
	return		void
	param		target		VertexAttribEnumNV in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float32 in array [count*4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4186
	offset		599

# ProgramParameterSigned4dNV(target, index, x, y, z, w)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  x		  Float64 in value
#	  param		  y		  Float64 in value
#	  param		  z		  Float64 in value
#	  param		  w		  Float64 in value
#	  category	  NV_vertex_program1_1_dcc
#	  version	  1.2
#	  vectorequiv	  ProgramParameterSigned4dvNV
#	  extension	  soft WINSOFT NV20
#	  offset	  ?
#
# ProgramParameterSigned4dvNV(target, index, v)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  v		  Float64 in array [4]
#	  category	  NV_vertex_program1_1_dcc
#	  version	  1.2
#	  extension	  soft WINSOFT NV20
#	  glxflags	  ignore
#	  offset	  ?
#
# ProgramParameterSigned4fNV(target, index, x, y, z, w)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  x		  Float32 in value
#	  param		  y		  Float32 in value
#	  param		  z		  Float32 in value
#	  param		  w		  Float32 in value
#	  category	  NV_vertex_program1_1_dcc
#	  version	  1.2
#	  vectorequiv	  ProgramParameterSigned4fvNV
#	  extension	  soft WINSOFT NV20
#	  offset	  ?
#
# ProgramParameterSigned4fvNV(target, index, v)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  v		  Float32 in array [4]
#	  category	  NV_vertex_program1_1_dcc
#	  version	  1.2
#	  extension	  soft WINSOFT NV20
#	  glxflags	  ignore
#	  offset	  ?
#
# ProgramParametersSigned4dvNV(target, index, count, v)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  count		  SizeI in value
#	  param		  v		  Float64 in array [count*4]
#	  category	  NV_vertex_program1_1_dcc
#	  version	  1.2
#	  extension	  soft WINSOFT NV20
#	  glxflags	  ignore
#	  offset	  ?
#
# ProgramParametersSigned4fvNV(target, index, count, v)
#	  return	  void
#	  param		  target	  VertexAttribEnumNV in value
#	  param		  index		  Int32 in value
#	  param		  count		  SizeI in value
#	  param		  v		  Float32 in array [count*4]
#	  category	  NV_vertex_program1_1_dcc
#	  version	  1.2
#	  extension	  soft WINSOFT NV20
#	  glxflags	  ignore
#	  offset	  ?

RequestResidentProgramsNV(n, programs)
	return		void
	param		n		SizeI in value
	param		programs	UInt32 in array [n]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4182
	offset		600

TrackMatrixNV(target, address, matrix, transform)
	return		void
	param		target		VertexAttribEnumNV in value
	param		address		UInt32 in value
	param		matrix		VertexAttribEnumNV in value
	param		transform	VertexAttribEnumNV in value
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4188
	offset		601

VertexAttribPointerNV(index, fsize, type, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		fsize		Int32 in value
	param		type		VertexAttribEnumNV in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(fsize/type/stride)] retained
	category	NV_vertex_program
	dlflags		notlistable
	version		1.2
	extension	soft WINSOFT NV10
	glxflags	ignore
	offset		602

VertexAttrib1dNV(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib1dvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib1d

VertexAttrib1dvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [1]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4197
	alias		VertexAttrib1dv

VertexAttrib1fNV(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib1fvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib1f

VertexAttrib1fvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [1]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4193
	alias		VertexAttrib1fv

VertexAttrib1sNV(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib1svNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib1s

VertexAttrib1svNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [1]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4189
	alias		VertexAttrib1sv

VertexAttrib2dNV(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib2dvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib2d

VertexAttrib2dvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [2]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4198
	alias		VertexAttrib2dv

VertexAttrib2fNV(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib2fvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib2f

VertexAttrib2fvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [2]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4194
	alias		VertexAttrib2fv

VertexAttrib2sNV(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib2svNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib2s

VertexAttrib2svNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [2]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4190
	alias		VertexAttrib2sv

VertexAttrib3dNV(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib3dvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib3d

VertexAttrib3dvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [3]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4199
	alias		VertexAttrib3dv

VertexAttrib3fNV(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib3fvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib3f

VertexAttrib3fvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [3]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4195
	alias		VertexAttrib3fv

VertexAttrib3sNV(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib3svNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib3s

VertexAttrib3svNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [3]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4191
	alias		VertexAttrib3sv

VertexAttrib4dNV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib4dvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib4d

VertexAttrib4dvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4200
	alias		VertexAttrib4dv

VertexAttrib4fNV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib4fvNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib4f

VertexAttrib4fvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float32 in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4196
	alias		VertexAttrib4fv

VertexAttrib4sNV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	param		w		Int16 in value
	category	NV_vertex_program
	version		1.2
	vectorequiv	VertexAttrib4svNV
	extension	soft WINSOFT NV10
	alias		VertexAttrib4s

VertexAttrib4svNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4192
	alias		VertexAttrib4sv

VertexAttrib4ubNV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		ColorUB in value
	param		y		ColorUB in value
	param		z		ColorUB in value
	param		w		ColorUB in value
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	vectorequiv	VertexAttrib4ubvNV
	alias		VertexAttrib4Nub

VertexAttrib4ubvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		ColorUB in array [4]
	category	NV_vertex_program
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4201
	alias		VertexAttrib4Nubv

VertexAttribs1dvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float64 in array [count]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4210
	offset		629

VertexAttribs1fvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float32 in array [count]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4206
	offset		630

VertexAttribs1svNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Int16 in array [count]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4202
	offset		631

VertexAttribs2dvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float64 in array [count*2]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4211
	offset		632

VertexAttribs2fvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float32 in array [count*2]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4207
	offset		633

VertexAttribs2svNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Int16 in array [count*2]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4203
	offset		634

VertexAttribs3dvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float64 in array [count*3]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4212
	offset		635

VertexAttribs3fvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float32 in array [count*3]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4208
	offset		636

VertexAttribs3svNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Int16 in array [count*3]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4204
	offset		637

VertexAttribs4dvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float64 in array [count*4]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4213
	offset		638

VertexAttribs4fvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Float32 in array [count*4]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4209
	offset		639

VertexAttribs4svNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		Int16 in array [count*4]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4205
	offset		640

VertexAttribs4ubvNV(index, count, v)
	return		void
	param		index		UInt32 in value
	param		count		SizeI in value
	param		v		ColorUB in array [count*4]
	category	NV_vertex_program
	dlflags		handcode
	version		1.2
	extension	soft WINSOFT NV10
	glxropcode	4214
	offset		641


###############################################################################
#
# Extension #234 - GLX_SGIX_visual_select_group
#
###############################################################################

###############################################################################
#
# Extension #235
# SGIX_texture_coordinate_clamp commands
#
###############################################################################

# (none)
newcategory: SGIX_texture_coordinate_clamp

###############################################################################
#
# Extension #236
# SGIX_scalebias_hint commands
#
###############################################################################

# (none)
newcategory: SGIX_scalebias_hint

###############################################################################
#
# Extension #237 - GLX_OML_swap_method commands
# Extension #238 - GLX_OML_sync_control commands
#
###############################################################################

###############################################################################
#
# Extension #239
# OML_interlace commands
#
###############################################################################

# (none)
newcategory: OML_interlace

###############################################################################
#
# Extension #240
# OML_subsample commands
#
###############################################################################

# (none)
newcategory: OML_subsample

###############################################################################
#
# Extension #241
# OML_resample commands
#
###############################################################################

# (none)
newcategory: OML_resample

###############################################################################
#
# Extension #242 - WGL_OML_sync_control commands
#
###############################################################################

###############################################################################
#
# Extension #243
# NV_copy_depth_to_color commands
#
###############################################################################

# (none)
newcategory: NV_copy_depth_to_color

###############################################################################
#
# Extension #244
# ATI_envmap_bumpmap commands
#
###############################################################################

TexBumpParameterivATI(pname, param)
	return		void
	param		pname		TexBumpParameterATI in value
	param		param		Int32 in array [COMPSIZE(pname)]
	category	ATI_envmap_bumpmap
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexBumpParameterfvATI(pname, param)
	return		void
	param		pname		TexBumpParameterATI in value
	param		param		Float32 in array [COMPSIZE(pname)]
	category	ATI_envmap_bumpmap
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetTexBumpParameterivATI(pname, param)
	return		void
	param		pname		GetTexBumpParameterATI in value
	param		param		Int32 out array [COMPSIZE(pname)]
	category	ATI_envmap_bumpmap
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetTexBumpParameterfvATI(pname, param)
	return		void
	param		pname		GetTexBumpParameterATI in value
	param		param		Float32 out array [COMPSIZE(pname)]
	category	ATI_envmap_bumpmap
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #245
# ATI_fragment_shader commands
#
###############################################################################

GenFragmentShadersATI(range)
	return		UInt32
	param		range		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindFragmentShaderATI(id)
	return		void
	param		id		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteFragmentShaderATI(id)
	return		void
	param		id		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BeginFragmentShaderATI()
	return		void
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EndFragmentShaderATI()
	return		void
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PassTexCoordATI(dst, coord, swizzle)
	return		void
	param		dst		UInt32 in value
	param		coord		UInt32 in value
	param		swizzle		SwizzleOpATI in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SampleMapATI(dst, interp, swizzle)
	return		void
	param		dst		UInt32 in value
	param		interp		UInt32 in value
	param		swizzle		SwizzleOpATI in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorFragmentOp1ATI(op, dst, dstMask, dstMod, arg1, arg1Rep, arg1Mod)
	return		void
	param		op		FragmentOpATI in value
	param		dst		UInt32 in value
	param		dstMask		UInt32 in value
	param		dstMod		UInt32 in value
	param		arg1		UInt32 in value
	param		arg1Rep		UInt32 in value
	param		arg1Mod		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorFragmentOp2ATI(op, dst, dstMask, dstMod, arg1, arg1Rep, arg1Mod, arg2, arg2Rep, arg2Mod)
	return		void
	param		op		FragmentOpATI in value
	param		dst		UInt32 in value
	param		dstMask		UInt32 in value
	param		dstMod		UInt32 in value
	param		arg1		UInt32 in value
	param		arg1Rep		UInt32 in value
	param		arg1Mod		UInt32 in value
	param		arg2		UInt32 in value
	param		arg2Rep		UInt32 in value
	param		arg2Mod		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorFragmentOp3ATI(op, dst, dstMask, dstMod, arg1, arg1Rep, arg1Mod, arg2, arg2Rep, arg2Mod, arg3, arg3Rep, arg3Mod)
	return		void
	param		op		FragmentOpATI in value
	param		dst		UInt32 in value
	param		dstMask		UInt32 in value
	param		dstMod		UInt32 in value
	param		arg1		UInt32 in value
	param		arg1Rep		UInt32 in value
	param		arg1Mod		UInt32 in value
	param		arg2		UInt32 in value
	param		arg2Rep		UInt32 in value
	param		arg2Mod		UInt32 in value
	param		arg3		UInt32 in value
	param		arg3Rep		UInt32 in value
	param		arg3Mod		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

AlphaFragmentOp1ATI(op, dst, dstMod, arg1, arg1Rep, arg1Mod)
	return		void
	param		op		FragmentOpATI in value
	param		dst		UInt32 in value
	param		dstMod		UInt32 in value
	param		arg1		UInt32 in value
	param		arg1Rep		UInt32 in value
	param		arg1Mod		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

AlphaFragmentOp2ATI(op, dst, dstMod, arg1, arg1Rep, arg1Mod, arg2, arg2Rep, arg2Mod)
	return		void
	param		op		FragmentOpATI in value
	param		dst		UInt32 in value
	param		dstMod		UInt32 in value
	param		arg1		UInt32 in value
	param		arg1Rep		UInt32 in value
	param		arg1Mod		UInt32 in value
	param		arg2		UInt32 in value
	param		arg2Rep		UInt32 in value
	param		arg2Mod		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

AlphaFragmentOp3ATI(op, dst, dstMod, arg1, arg1Rep, arg1Mod, arg2, arg2Rep, arg2Mod, arg3, arg3Rep, arg3Mod)
	return		void
	param		op		FragmentOpATI in value
	param		dst		UInt32 in value
	param		dstMod		UInt32 in value
	param		arg1		UInt32 in value
	param		arg1Rep		UInt32 in value
	param		arg1Mod		UInt32 in value
	param		arg2		UInt32 in value
	param		arg2Rep		UInt32 in value
	param		arg2Mod		UInt32 in value
	param		arg3		UInt32 in value
	param		arg3Rep		UInt32 in value
	param		arg3Mod		UInt32 in value
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SetFragmentShaderConstantATI(dst, value)
	return		void
	param		dst		UInt32 in value
	param		value		ConstFloat32 in array [4]
	category	ATI_fragment_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #246
# ATI_pn_triangles commands
#
###############################################################################

PNTrianglesiATI(pname, param)
	return		void
	param		pname		PNTrianglesPNameATI in value
	param		param		Int32 in value
	category	ATI_pn_triangles
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PNTrianglesfATI(pname, param)
	return		void
	param		pname		PNTrianglesPNameATI in value
	param		param		Float32 in value
	category	ATI_pn_triangles
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #247
# ATI_vertex_array_object commands
#
###############################################################################

NewObjectBufferATI(size, pointer, usage)
	return		UInt32
	param		size		SizeI in value
	param		pointer		ConstVoid in array [size]
	param		usage		ArrayObjectUsageATI in value
	category	ATI_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsObjectBufferATI(buffer)
	return		Boolean
	param		buffer		UInt32 in value
	category	ATI_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UpdateObjectBufferATI(buffer, offset, size, pointer, preserve)
	return		void
	param		buffer		UInt32 in value
	param		offset		UInt32 in value
	param		size		SizeI in value
	param		pointer		ConstVoid in array [size]
	param		preserve	PreserveModeATI in value
	category	ATI_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetObjectBufferfvATI(buffer, pname, params)
	return		void
	param		buffer		UInt32 in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Float32 out array [1]
	category	ATI_vertex_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetObjectBufferivATI(buffer, pname, params)
	return		void
	param		buffer		UInt32 in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Int32 out array [1]
	category	ATI_vertex_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

FreeObjectBufferATI(buffer)
	return		void
	param		buffer		UInt32 in value
	category	ATI_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ArrayObjectATI(array, size, type, stride, buffer, offset)
	return		void
	param		array		EnableCap in value
	param		size		Int32 in value
	param		type		ScalarType in value
	param		stride		SizeI in value
	param		buffer		UInt32 in value
	param		offset		UInt32 in value
	category	ATI_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetArrayObjectfvATI(array, pname, params)
	return		void
	param		array		EnableCap in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Float32 out array [1]
	category	ATI_vertex_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetArrayObjectivATI(array, pname, params)
	return		void
	param		array		EnableCap in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Int32 out array [1]
	category	ATI_vertex_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

VariantArrayObjectATI(id, type, stride, buffer, offset)
	return		void
	param		id		UInt32 in value
	param		type		ScalarType in value
	param		stride		SizeI in value
	param		buffer		UInt32 in value
	param		offset		UInt32 in value
	category	ATI_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVariantArrayObjectfvATI(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Float32 out array [1]
	category	ATI_vertex_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVariantArrayObjectivATI(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Int32 out array [1]
	category	ATI_vertex_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #248
# EXT_vertex_shader commands
#
###############################################################################

BeginVertexShaderEXT()
	return		void
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EndVertexShaderEXT()
	return		void
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindVertexShaderEXT(id)
	return		void
	param		id		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GenVertexShadersEXT(range)
	return		UInt32
	param		range		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteVertexShaderEXT(id)
	return		void
	param		id		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ShaderOp1EXT(op, res, arg1)
	return		void
	param		op		VertexShaderOpEXT in value
	param		res		UInt32 in value
	param		arg1		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ShaderOp2EXT(op, res, arg1, arg2)
	return		void
	param		op		VertexShaderOpEXT in value
	param		res		UInt32 in value
	param		arg1		UInt32 in value
	param		arg2		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ShaderOp3EXT(op, res, arg1, arg2, arg3)
	return		void
	param		op		VertexShaderOpEXT in value
	param		res		UInt32 in value
	param		arg1		UInt32 in value
	param		arg2		UInt32 in value
	param		arg3		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SwizzleEXT(res, in, outX, outY, outZ, outW)
	return		void
	param		res		UInt32 in value
	param		in		UInt32 in value
	param		outX		VertexShaderCoordOutEXT in value
	param		outY		VertexShaderCoordOutEXT in value
	param		outZ		VertexShaderCoordOutEXT in value
	param		outW		VertexShaderCoordOutEXT in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

WriteMaskEXT(res, in, outX, outY, outZ, outW)
	return		void
	param		res		UInt32 in value
	param		in		UInt32 in value
	param		outX		VertexShaderWriteMaskEXT in value
	param		outY		VertexShaderWriteMaskEXT in value
	param		outZ		VertexShaderWriteMaskEXT in value
	param		outW		VertexShaderWriteMaskEXT in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

InsertComponentEXT(res, src, num)
	return		void
	param		res		UInt32 in value
	param		src		UInt32 in value
	param		num		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ExtractComponentEXT(res, src, num)
	return		void
	param		res		UInt32 in value
	param		src		UInt32 in value
	param		num		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GenSymbolsEXT(datatype, storagetype, range, components)
	return		UInt32
	param		datatype	DataTypeEXT in value
	param		storagetype	VertexShaderStorageTypeEXT in value
	param		range		ParameterRangeEXT in value
	param		components	UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SetInvariantEXT(id, type, addr)
	return		void
	param		id		UInt32 in value
	param		type		ScalarType in value
	param		addr		Void in array [COMPSIZE(id/type)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SetLocalConstantEXT(id, type, addr)
	return		void
	param		id		UInt32 in value
	param		type		ScalarType in value
	param		addr		Void in array [COMPSIZE(id/type)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantbvEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		Int8 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantsvEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		Int16 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantivEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		Int32 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantfvEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		Float32 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantdvEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		Float64 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantubvEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		UInt8 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantusvEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		UInt16 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantuivEXT(id, addr)
	return		void
	param		id		UInt32 in value
	param		addr		UInt32 in array [COMPSIZE(id)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VariantPointerEXT(id, type, stride, addr)
	return		void
	param		id		UInt32 in value
	param		type		ScalarType in value
	param		stride		UInt32 in value
	param		addr		Void in array [COMPSIZE(id/type/stride)]
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EnableVariantClientStateEXT(id)
	return		void
	param		id		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DisableVariantClientStateEXT(id)
	return		void
	param		id		UInt32 in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindLightParameterEXT(light, value)
	return		UInt32
	param		light		LightName in value
	param		value		LightParameter in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindMaterialParameterEXT(face, value)
	return		UInt32
	param		face		MaterialFace in value
	param		value		MaterialParameter in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindTexGenParameterEXT(unit, coord, value)
	return		UInt32
	param		unit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		value		TextureGenParameter in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindTextureUnitParameterEXT(unit, value)
	return		UInt32
	param		unit		TextureUnit in value
	param		value		VertexShaderTextureUnitParameter in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindParameterEXT(value)
	return		UInt32
	param		value		VertexShaderParameterEXT in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsVariantEnabledEXT(id, cap)
	return		Boolean
	param		id		UInt32 in value
	param		cap		VariantCapEXT in value
	category	EXT_vertex_shader
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVariantBooleanvEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Boolean out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVariantIntegervEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Int32 out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVariantFloatvEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Float32 out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVariantPointervEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		VoidPointer out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetInvariantBooleanvEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Boolean out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetInvariantIntegervEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Int32 out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetInvariantFloatvEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Float32 out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetLocalConstantBooleanvEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Boolean out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetLocalConstantIntegervEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Int32 out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetLocalConstantFloatvEXT(id, value, data)
	return		void
	param		id		UInt32 in value
	param		value		GetVariantValueEXT in value
	param		data		Float32 out array [COMPSIZE(id)]
	category	EXT_vertex_shader
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #249
# ATI_vertex_streams commands
#
###############################################################################

VertexStream1sATI(stream, x)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int16 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1svATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int16 in array [1]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1iATI(stream, x)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1ivATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int32 in array [1]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1fATI(stream, x)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1fvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float32 in array [1]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1dATI(stream, x)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float64 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream1dvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float64 in array [1]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2sATI(stream, x, y)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int16 in value
	param		y		Int16 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2svATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int16 in array [2]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2iATI(stream, x, y)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int32 in value
	param		y		Int32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2ivATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int32 in array [2]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2fATI(stream, x, y)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2fvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float32 in array [2]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2dATI(stream, x, y)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream2dvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float64 in array [2]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3sATI(stream, x, y, z)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3svATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int16 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3iATI(stream, x, y, z)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3ivATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int32 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3fATI(stream, x, y, z)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3fvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float32 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3dATI(stream, x, y, z)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream3dvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float64 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4sATI(stream, x, y, z, w)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int16 in value
	param		y		Int16 in value
	param		z		Int16 in value
	param		w		Int16 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4svATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int16 in array [4]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4iATI(stream, x, y, z, w)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	param		w		Int32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4ivATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int32 in array [4]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4fATI(stream, x, y, z, w)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4fvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float32 in array [4]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4dATI(stream, x, y, z, w)
	return		void
	param		stream		VertexStreamATI in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexStream4dvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float64 in array [4]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3bATI(stream, nx, ny, nz)
	return		void
	param		stream		VertexStreamATI in value
	param		nx		Int8 in value
	param		ny		Int8 in value
	param		nz		Int8 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3bvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int8 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3sATI(stream, nx, ny, nz)
	return		void
	param		stream		VertexStreamATI in value
	param		nx		Int16 in value
	param		ny		Int16 in value
	param		nz		Int16 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3svATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int16 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3iATI(stream, nx, ny, nz)
	return		void
	param		stream		VertexStreamATI in value
	param		nx		Int32 in value
	param		ny		Int32 in value
	param		nz		Int32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3ivATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Int32 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3fATI(stream, nx, ny, nz)
	return		void
	param		stream		VertexStreamATI in value
	param		nx		Float32 in value
	param		ny		Float32 in value
	param		nz		Float32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3fvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float32 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3dATI(stream, nx, ny, nz)
	return		void
	param		stream		VertexStreamATI in value
	param		nx		Float64 in value
	param		ny		Float64 in value
	param		nz		Float64 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalStream3dvATI(stream, coords)
	return		void
	param		stream		VertexStreamATI in value
	param		coords		Float64 in array [3]
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClientActiveVertexStreamATI(stream)
	return		void
	param		stream		VertexStreamATI in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexBlendEnviATI(pname, param)
	return		void
	param		pname		VertexStreamATI in value
	param		param		Int32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexBlendEnvfATI(pname, param)
	return		void
	param		pname		VertexStreamATI in value
	param		param		Float32 in value
	category	ATI_vertex_streams
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #250 - WGL_I3D_digital_video_control
# Extension #251 - WGL_I3D_gamma
# Extension #252 - WGL_I3D_genlock
# Extension #253 - WGL_I3D_image_buffer
# Extension #254 - WGL_I3D_swap_frame_lock
# Extension #255 - WGL_I3D_swap_frame_usage
#
###############################################################################

###############################################################################
#
# Extension #256
# ATI_element_array commands
#
###############################################################################

ElementPointerATI(type, pointer)
	return		void
	param		type		ElementPointerTypeATI in value
	param		pointer		Void in array [COMPSIZE(type)] retained
	category	ATI_element_array
	dlflags		notlistable
	glxflags	client-handcode client-intercept server-handcode
	version		1.2
	offset		?

DrawElementArrayATI(mode, count)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in value
	category	ATI_element_array
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.2
	offset		?

DrawRangeElementArrayATI(mode, start, end, count)
	return		void
	param		mode		PrimitiveType in value
	param		start		UInt32 in value
	param		end		UInt32 in value
	param		count		SizeI in value
	category	ATI_element_array
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.2
	offset		?

###############################################################################
#
# Extension #257
# SUN_mesh_array commands
#
###############################################################################

DrawMeshArraysSUN(mode, first, count, width)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in value
	param		count		SizeI in value
	param		width		SizeI in value
	category	SUN_mesh_array
	dlflags		handcode
	glxflags	client-handcode client-intercept server-handcode
	version		1.1
	glxropcode	?
	offset		?

###############################################################################
#
# Extension #258
# SUN_slice_accum commands
#
###############################################################################

# (none)
newcategory: SUN_slice_accum

###############################################################################
#
# Extension #259
# NV_multisample_filter_hint commands
#
###############################################################################

# (none)
newcategory: NV_multisample_filter_hint

###############################################################################
#
# Extension #260
# NV_depth_clamp commands
#
###############################################################################

# (none)
newcategory: NV_depth_clamp

###############################################################################
#
# Extension #261
# NV_occlusion_query commands
#
###############################################################################

GenOcclusionQueriesNV(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 out array [n]
	dlflags		notlistable
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

DeleteOcclusionQueriesNV(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 in array [n]
	dlflags		notlistable
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

IsOcclusionQueryNV(id)
	return		Boolean
	param		id		UInt32 in value
	dlflags		notlistable
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

BeginOcclusionQueryNV(id)
	return		void
	param		id		UInt32 in value
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

EndOcclusionQueryNV()
	return		void
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

GetOcclusionQueryivNV(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		OcclusionQueryParameterNameNV in value
	param		params		Int32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

GetOcclusionQueryuivNV(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		OcclusionQueryParameterNameNV in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	dlflags		notlistable
	category	NV_occlusion_query
	version		1.2
	extension	soft WINSOFT NV20
	glxflags	ignore

###############################################################################
#
# Extension #262
# NV_point_sprite commands
#
###############################################################################

PointParameteriNV(pname, param)
	return		void
	param		pname		PointParameterNameARB in value
	param		param		Int32 in value
	category	NV_point_sprite
	version		1.2
	extension	soft WINSOFT NV20
	glxropcode	4221
	alias		PointParameteri

PointParameterivNV(pname, params)
	return		void
	param		pname		PointParameterNameARB in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	NV_point_sprite
	version		1.2
	extension	soft WINSOFT NV20
	glxropcode	4222
	alias		PointParameteriv

###############################################################################
#
# Extension #263 - WGL_NV_render_depth_texture
# Extension #264 - WGL_NV_render_texture_rectangle
#
###############################################################################

###############################################################################
#
# Extension #265
# NV_texture_shader3 commands
#
###############################################################################

# (none)
newcategory: NV_texture_shader3

###############################################################################
#
# Extension #266
# NV_vertex_program1_1 commands
#
###############################################################################

# (none)
newcategory: NV_vertex_program1_1

###############################################################################
#
# Extension #267
# EXT_shadow_funcs commands
#
###############################################################################

# (none)
newcategory: EXT_shadow_funcs

###############################################################################
#
# Extension #268
# EXT_stencil_two_side commands
#
###############################################################################

ActiveStencilFaceEXT(face)
	return		void
	param		face		StencilFaceDirection in value
	category	EXT_stencil_two_side
	version		1.3
	glxropcode	4220
	offset		646

###############################################################################
#
# Extension #269
# ATI_text_fragment_shader commands
#
###############################################################################

# Uses ARB_vertex_program entry points
newcategory: ATI_text_fragment_shader

###############################################################################
#
# Extension #270
# APPLE_client_storage commands
#
###############################################################################

# (none)
newcategory: APPLE_client_storage

###############################################################################
#
# Extension #271
# APPLE_element_array commands
#
###############################################################################

ElementPointerAPPLE(type, pointer)
	return		void
	param		type		ElementPointerTypeATI in value
	param		pointer		Void in array [type]
	category	APPLE_element_array
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawElementArrayAPPLE(mode, first, count)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in value
	param		count		SizeI in value
	category	APPLE_element_array
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DrawRangeElementArrayAPPLE(mode, start, end, first, count)
	return		void
	param		mode		PrimitiveType in value
	param		start		UInt32 in value
	param		end		UInt32 in value
	param		first		Int32 in value
	param		count		SizeI in value
	category	APPLE_element_array
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiDrawElementArrayAPPLE(mode, first, count, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		first		Int32 in array [primcount]
	param		count		SizeI in array [primcount]
	param		primcount	SizeI in value
	category	APPLE_element_array
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiDrawRangeElementArrayAPPLE(mode, start, end, first, count, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		start		UInt32 in value
	param		end		UInt32 in value
	param		first		Int32 in array [primcount]
	param		count		SizeI in array [primcount]
	param		primcount	SizeI in value
	category	APPLE_element_array
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #272
# APPLE_fence commands
#
###############################################################################

GenFencesAPPLE(n, fences)
	return		void
	param		n		SizeI in value
	param		fences		FenceNV out array [n]
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteFencesAPPLE(n, fences)
	return		void
	param		n		SizeI in value
	param		fences		FenceNV in array [n]
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SetFenceAPPLE(fence)
	return		void
	param		fence		FenceNV in value
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsFenceAPPLE(fence)
	return		Boolean
	param		fence		FenceNV in value
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TestFenceAPPLE(fence)
	return		Boolean
	param		fence		FenceNV in value
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FinishFenceAPPLE(fence)
	return		void
	param		fence		FenceNV in value
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TestObjectAPPLE(object, name)
	return		Boolean
	param		object		ObjectTypeAPPLE in value
	param		name		UInt32 in value
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FinishObjectAPPLE(object, name)
	return		void
	param		object		ObjectTypeAPPLE in value
	param		name		Int32 in value
	category	APPLE_fence
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #273
# APPLE_vertex_array_object commands
#
###############################################################################

BindVertexArrayAPPLE(array)
	return		void
	param		array		UInt32 in value
	category	APPLE_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		BindVertexArray

DeleteVertexArraysAPPLE(n, arrays)
	return		void
	param		n		SizeI in value
	param		arrays		UInt32 in array [n]
	category	APPLE_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		DeleteVertexArrays

GenVertexArraysAPPLE(n, arrays)
	return		void
	param		n		SizeI in value
	param		arrays		UInt32 out array [n]
	category	APPLE_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		GenVertexArray

IsVertexArrayAPPLE(array)
	return		Boolean
	param		array		UInt32 in value
	category	APPLE_vertex_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		IsVertexArray

###############################################################################
#
# Extension #274
# APPLE_vertex_array_range commands
#
###############################################################################

VertexArrayRangeAPPLE(length, pointer)
	return		void
	param		length		SizeI in value
	param		pointer		Void out array [length]
	category	APPLE_vertex_array_range
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FlushVertexArrayRangeAPPLE(length, pointer)
	return		void
	param		length		SizeI in value
	param		pointer		Void out array [length]
	category	APPLE_vertex_array_range
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexArrayParameteriAPPLE(pname, param)
	return		void
	param		pname		VertexArrayPNameAPPLE in value
	param		param		Int32 in value
	category	APPLE_vertex_array_range
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #275
# APPLE_ycbcr_422 commands
#
###############################################################################

# (none)
newcategory: APPLE_ycbcr_422

###############################################################################
#
# Extension #276
# S3_s3tc commands
#
###############################################################################

# (none)
newcategory: S3_s3tc

###############################################################################
#
# Extension #277
# ATI_draw_buffers commands
#
###############################################################################

DrawBuffersATI(n, bufs)
	return		void
	param		n		SizeI in value
	param		bufs		DrawBufferModeATI in array [n]
	category	ATI_draw_buffers
	version		1.2
	extension
	glxropcode	233
	alias		DrawBuffers

###############################################################################
#
# Extension #278 - WGL_ATI_pixel_format_float
#
###############################################################################

newcategory: ATI_pixel_format_float
passthru: /* This is really a WGL extension, but defines some associated GL enums.
passthru:  * ATI does not export "GL_ATI_pixel_format_float" in the GL_EXTENSIONS string.
passthru:  */

###############################################################################
#
# Extension #279
# ATI_texture_env_combine3 commands
#
###############################################################################

# (none)
newcategory: ATI_texture_env_combine3

###############################################################################
#
# Extension #280
# ATI_texture_float commands
#
###############################################################################

# (none)
newcategory: ATI_texture_float

###############################################################################
#
# Extension #281 (also WGL_NV_float_buffer)
# NV_float_buffer commands
#
###############################################################################

# (none)
newcategory: NV_float_buffer

###############################################################################
#
# Extension #282
# NV_fragment_program commands
#
###############################################################################

# Some NV_fragment_program entry points are shared with ARB_vertex_program,
#   and are only included in that #define block, for now.
newcategory: NV_fragment_program
passthru: /* Some NV_fragment_program entry points are shared with ARB_vertex_program. */

ProgramNamedParameter4fNV(id, len, name, x, y, z, w)
	return		void
	param		id		UInt32 in value
	param		len		SizeI in value
	param		name		UInt8 in array [1]
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	NV_fragment_program
	version		1.2
	extension
	vectorequiv	ProgramNamedParameter4fvNV
	glxvectorequiv	ProgramNamedParameter4fvNV
	offset		682

ProgramNamedParameter4fvNV(id, len, name, v)
	return		void
	param		id		UInt32 in value
	param		len		SizeI in value
	param		name		UInt8 in array [1]
	param		v		Float32 in array [4]
	category	NV_fragment_program
	version		1.2
	extension
	glxropcode	4218
	glxflags	ignore
	offset		684

ProgramNamedParameter4dNV(id, len, name, x, y, z, w)
	return		void
	param		id		UInt32 in value
	param		len		SizeI in value
	param		name		UInt8 in array [1]
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	NV_fragment_program
	version		1.2
	extension
	vectorequiv	ProgramNamedParameter4dvNV
	glxvectorequiv	ProgramNamedParameter4dvNV
	offset		683

ProgramNamedParameter4dvNV(id, len, name, v)
	return		void
	param		id		UInt32 in value
	param		len		SizeI in value
	param		name		UInt8 in array [1]
	param		v		Float64 in array [4]
	category	NV_fragment_program
	version		1.2
	extension
	glxropcode	4219
	glxflags	ignore
	offset		685

GetProgramNamedParameterfvNV(id, len, name, params)
	return		void
	param		id		UInt32 in value
	param		len		SizeI in value
	param		name		UInt8 in array [1]
	param		params		Float32 out array [4]
	category	NV_fragment_program
	dlflags		notlistable
	version		1.2
	extension
	glxvendorpriv	1310
	glxflags	ignore
	offset		686

GetProgramNamedParameterdvNV(id, len, name, params)
	return		void
	param		id		UInt32 in value
	param		len		SizeI in value
	param		name		UInt8 in array [1]
	param		params		Float64 out array [4]
	category	NV_fragment_program
	dlflags		notlistable
	version		1.2
	extension
	glxvendorpriv	1311
	glxflags	ignore
	offset		687

###############################################################################
#
# Extension #283
# NV_half_float commands
#
###############################################################################

Vertex2hNV(x, y)
	return		void
	param		x		Half16NV in value
	param		y		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	Vertex2hvNV
	glxvectorequiv	Vertex2hvNV
	offset		?

Vertex2hvNV(v)
	return		void
	param		v		Half16NV in array [2]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4240
	glxflags	ignore
	offset		?

Vertex3hNV(x, y, z)
	return		void
	param		x		Half16NV in value
	param		y		Half16NV in value
	param		z		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	Vertex3hvNV
	glxvectorequiv	Vertex3hvNV
	offset		?

Vertex3hvNV(v)
	return		void
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4241
	glxflags	ignore
	offset		?

Vertex4hNV(x, y, z, w)
	return		void
	param		x		Half16NV in value
	param		y		Half16NV in value
	param		z		Half16NV in value
	param		w		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	Vertex4hvNV
	glxvectorequiv	Vertex4hvNV
	offset		?

Vertex4hvNV(v)
	return		void
	param		v		Half16NV in array [4]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4242
	glxflags	ignore
	offset		?

Normal3hNV(nx, ny, nz)
	return		void
	param		nx		Half16NV in value
	param		ny		Half16NV in value
	param		nz		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	Normal3hvNV
	glxvectorequiv	Normal3hvNV
	offset		?

Normal3hvNV(v)
	return		void
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4243
	glxflags	ignore
	offset		?

Color3hNV(red, green, blue)
	return		void
	param		red		Half16NV in value
	param		green		Half16NV in value
	param		blue		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	Color3hvNV
	glxvectorequiv	Color3hvNV
	offset		?

Color3hvNV(v)
	return		void
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4244
	glxflags	ignore
	offset		?

Color4hNV(red, green, blue, alpha)
	return		void
	param		red		Half16NV in value
	param		green		Half16NV in value
	param		blue		Half16NV in value
	param		alpha		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	Color4hvNV
	glxvectorequiv	Color4hvNV
	offset		?

Color4hvNV(v)
	return		void
	param		v		Half16NV in array [4]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4245
	glxflags	ignore
	offset		?

TexCoord1hNV(s)
	return		void
	param		s		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	TexCoord1hvNV
	glxvectorequiv	TexCoord1hvNV
	offset		?

TexCoord1hvNV(v)
	return		void
	param		v		Half16NV in array [1]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4246
	glxflags	ignore
	offset		?

TexCoord2hNV(s, t)
	return		void
	param		s		Half16NV in value
	param		t		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	TexCoord2hvNV
	glxvectorequiv	TexCoord2hvNV
	offset		?

TexCoord2hvNV(v)
	return		void
	param		v		Half16NV in array [2]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4247
	glxflags	ignore
	offset		?

TexCoord3hNV(s, t, r)
	return		void
	param		s		Half16NV in value
	param		t		Half16NV in value
	param		r		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	TexCoord3hvNV
	glxvectorequiv	TexCoord3hvNV
	offset		?

TexCoord3hvNV(v)
	return		void
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4248
	glxflags	ignore
	offset		?

TexCoord4hNV(s, t, r, q)
	return		void
	param		s		Half16NV in value
	param		t		Half16NV in value
	param		r		Half16NV in value
	param		q		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	TexCoord4hvNV
	glxvectorequiv	TexCoord4hvNV
	offset		?

TexCoord4hvNV(v)
	return		void
	param		v		Half16NV in array [4]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4249
	glxflags	ignore
	offset		?

MultiTexCoord1hNV(target, s)
	return		void
	param		target		TextureUnit in value
	param		s		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	MultiTexCoord1hvNV
	glxvectorequiv	MultiTexCoord1hvNV
	offset		?

MultiTexCoord1hvNV(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		Half16NV in array [1]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4250
	glxflags	ignore
	offset		?

MultiTexCoord2hNV(target, s, t)
	return		void
	param		target		TextureUnit in value
	param		s		Half16NV in value
	param		t		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	MultiTexCoord2hvNV
	glxvectorequiv	MultiTexCoord2hvNV
	offset		?

MultiTexCoord2hvNV(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		Half16NV in array [2]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4251
	glxflags	ignore
	offset		?

MultiTexCoord3hNV(target, s, t, r)
	return		void
	param		target		TextureUnit in value
	param		s		Half16NV in value
	param		t		Half16NV in value
	param		r		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	MultiTexCoord3hvNV
	glxvectorequiv	MultiTexCoord3hvNV
	offset		?

MultiTexCoord3hvNV(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4252
	glxflags	ignore
	offset		?

MultiTexCoord4hNV(target, s, t, r, q)
	return		void
	param		target		TextureUnit in value
	param		s		Half16NV in value
	param		t		Half16NV in value
	param		r		Half16NV in value
	param		q		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	MultiTexCoord4hvNV
	glxvectorequiv	MultiTexCoord4hvNV
	offset		?

MultiTexCoord4hvNV(target, v)
	return		void
	param		target		TextureUnit in value
	param		v		Half16NV in array [4]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4253
	glxflags	ignore
	offset		?

FogCoordhNV(fog)
	return		void
	param		fog		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	FogCoordhvNV
	glxvectorequiv	FogCoordhvNV
	offset		?

FogCoordhvNV(fog)
	return		void
	param		fog		Half16NV in array [1]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4254
	glxflags	ignore
	offset		?

SecondaryColor3hNV(red, green, blue)
	return		void
	param		red		Half16NV in value
	param		green		Half16NV in value
	param		blue		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	SecondaryColor3hvNV
	glxvectorequiv	SecondaryColor3hvNV
	offset		?

SecondaryColor3hvNV(v)
	return		void
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4255
	glxflags	ignore
	offset		?

VertexWeighthNV(weight)
	return		void
	param		weight		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	VertexWeighthvNV
	glxvectorequiv	VertexWeighthvNV
	offset		?

VertexWeighthvNV(weight)
	return		void
	param		weight		Half16NV in array [1]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4256
	glxflags	ignore
	offset		?

VertexAttrib1hNV(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	VertexAttrib1hvNV
	glxvectorequiv	VertexAttrib1hvNV
	offset		?

VertexAttrib1hvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Half16NV in array [1]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4257
	glxflags	ignore
	offset		?

VertexAttrib2hNV(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Half16NV in value
	param		y		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	VertexAttrib2hvNV
	glxvectorequiv	VertexAttrib2hvNV
	offset		?

VertexAttrib2hvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Half16NV in array [2]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4258
	glxflags	ignore
	offset		?

VertexAttrib3hNV(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Half16NV in value
	param		y		Half16NV in value
	param		z		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	VertexAttrib3hvNV
	glxvectorequiv	VertexAttrib3hvNV
	offset		?

VertexAttrib3hvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Half16NV in array [3]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4259
	glxflags	ignore
	offset		?

VertexAttrib4hNV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Half16NV in value
	param		y		Half16NV in value
	param		z		Half16NV in value
	param		w		Half16NV in value
	category	NV_half_float
	version		1.2
	extension
	vectorequiv	VertexAttrib4hvNV
	glxvectorequiv	VertexAttrib4hvNV
	offset		?

VertexAttrib4hvNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Half16NV in array [4]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4260
	glxflags	ignore
	offset		?

VertexAttribs1hvNV(index, n, v)
	return		void
	param		index		UInt32 in value
	param		n		SizeI in value
	param		v		Half16NV in array [n]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4261
	glxflags	ignore
	offset		?

VertexAttribs2hvNV(index, n, v)
	return		void
	param		index		UInt32 in value
	param		n		SizeI in value
	param		v		Half16NV in array [n]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4262
	glxflags	ignore
	offset		?

VertexAttribs3hvNV(index, n, v)
	return		void
	param		index		UInt32 in value
	param		n		SizeI in value
	param		v		Half16NV in array [n]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4263
	glxflags	ignore
	offset		?

VertexAttribs4hvNV(index, n, v)
	return		void
	param		index		UInt32 in value
	param		n		SizeI in value
	param		v		Half16NV in array [n]
	category	NV_half_float
	version		1.2
	extension
	glxropcode	4264
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #284
# NV_pixel_data_range commands
#
###############################################################################

PixelDataRangeNV(target, length, pointer)
	return		void
	param		target		PixelDataRangeTargetNV in value
	param		length		SizeI in value
	param		pointer		Void in array [length]
	category	NV_pixel_data_range
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FlushPixelDataRangeNV(target)
	return		void
	param		target		PixelDataRangeTargetNV in value
	category	NV_pixel_data_range
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #285
# NV_primitive_restart commands
#
###############################################################################

PrimitiveRestartNV()
	return		void
	category	NV_primitive_restart
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PrimitiveRestartIndexNV(index)
	return		void
	param		index		UInt32 in value
	category	NV_primitive_restart
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?


###############################################################################
#
# Extension #286
# NV_texture_expand_normal commands
#
###############################################################################

# (none)
newcategory: NV_texture_expand_normal

###############################################################################
#
# Extension #287
# NV_vertex_program2 commands
#
###############################################################################

# (none)
newcategory: NV_vertex_program2

###############################################################################
#
# Extension #288
# ATI_map_object_buffer commands
#
###############################################################################

MapObjectBufferATI(buffer)
	return		VoidPointer
	param		buffer		UInt32 in value
	category	ATI_map_object_buffer
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UnmapObjectBufferATI(buffer)
	return		void
	param		buffer		UInt32 in value
	category	ATI_map_object_buffer
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #289
# ATI_separate_stencil commands
#
###############################################################################

StencilOpSeparateATI(face, sfail, dpfail, dppass)
	return		void
	param		face		StencilFaceDirection in value
	param		sfail		StencilOp in value
	param		dpfail		StencilOp in value
	param		dppass		StencilOp in value
	category	ATI_separate_stencil
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		StencilOpSeparate

StencilFuncSeparateATI(frontfunc, backfunc, ref, mask)
	return		void
	param		frontfunc	StencilFunction in value
	param		backfunc	StencilFunction in value
	param		ref		ClampedStencilValue in value
	param		mask		MaskedStencilValue in value
	category	ATI_separate_stencil
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	alias		StencilFuncSeparate

###############################################################################
#
# Extension #290
# ATI_vertex_attrib_array_object commands
#
###############################################################################

VertexAttribArrayObjectATI(index, size, type, normalized, stride, buffer, offset)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		VertexAttribPointerTypeARB in value
	param		normalized	Boolean in value
	param		stride		SizeI in value
	param		buffer		UInt32 in value
	param		offset		UInt32 in value
	category	ATI_vertex_attrib_array_object
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVertexAttribArrayObjectfvATI(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Float32 out array [pname]
	category	ATI_vertex_attrib_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVertexAttribArrayObjectivATI(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		ArrayObjectPNameATI in value
	param		params		Int32 out array [pname]
	category	ATI_vertex_attrib_array_object
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #291
# OES_byte_coordinates commands
#
###############################################################################

MultiTexCoord1bOES(texture, s)
	return		void
	param		texture		GLenum in value
	param		s		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord1bvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstByte in array [1]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord2bOES(texture, s, t)
	return		void
	param		texture		GLenum in value
	param		s		Int8 in value
	param		t		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord2bvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstByte in array [2]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord3bOES(texture, s, t, r)
	return		void
	param		texture		GLenum in value
	param		s		Int8 in value
	param		t		Int8 in value
	param		r		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord3bvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstByte in array [3]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord4bOES(texture, s, t, r, q)
	return		void
	param		texture		GLenum in value
	param		s		Int8 in value
	param		t		Int8 in value
	param		r		Int8 in value
	param		q		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord4bvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstByte in array [4]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord1bOES(s)
	return		void
	param		s		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord1bvOES(coords)
	return		void
	param		coords		ConstByte in array [1]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord2bOES(s, t)
	return		void
	param		s		Int8 in value
	param		t		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord2bvOES(coords)
	return		void
	param		coords		ConstByte in array [2]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord3bOES(s, t, r)
	return		void
	param		s		Int8 in value
	param		t		Int8 in value
	param		r		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord3bvOES(coords)
	return		void
	param		coords		ConstByte in array [3]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord4bOES(s, t, r, q)
	return		void
	param		s		Int8 in value
	param		t		Int8 in value
	param		r		Int8 in value
	param		q		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord4bvOES(coords)
	return		void
	param		coords		ConstByte in array [4]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex2bOES(x)
	return		void
	param		x		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex2bvOES(coords)
	return		void
	param		coords		ConstByte in array [2]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex3bOES(x, y)
	return		void
	param		x		Int8 in value
	param		y		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex3bvOES(coords)
	return		void
	param		coords		ConstByte in array [3]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex4bOES(x, y, z)
	return		void
	param		x		Int8 in value
	param		y		Int8 in value
	param		z		Int8 in value
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex4bvOES(coords)
	return		void
	param		coords		ConstByte in array [4]
	category	OES_byte_coordinates
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #292
# OES_fixed_point commands
#
###############################################################################

# ??? VERIFY DONE ???
## Many of these are compatibility profile only

AccumxOES(op, value)
	return		void
	param		op		GLenum in value
	param		value		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

AlphaFuncxOES(func, ref)
	return		void
	param		func		GLenum in value
	param		ref		ClampedFixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BitmapxOES(width, height, xorig, yorig, xmove, ymove, bitmap)
	return		void
	param		width		SizeI in value
	param		height		SizeI in value
	param		xorig		Fixed in value
	param		yorig		Fixed in value
	param		xmove		Fixed in value
	param		ymove		Fixed in value
	param		bitmap		ConstUByte in array [COMPSIZE()]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendColorxOES(red, green, blue, alpha)
	return		void
	param		red		ClampedFixed in value
	param		green		ClampedFixed in value
	param		blue		ClampedFixed in value
	param		alpha		ClampedFixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearAccumxOES(red, green, blue, alpha)
	return		void
	param		red		ClampedFixed in value
	param		green		ClampedFixed in value
	param		blue		ClampedFixed in value
	param		alpha		ClampedFixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearColorxOES(red, green, blue, alpha)
	return		void
	param		red		ClampedFixed in value
	param		green		ClampedFixed in value
	param		blue		ClampedFixed in value
	param		alpha		ClampedFixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearDepthxOES(depth)
	return		void
	param		depth		ClampedFixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClipPlanexOES(plane, equation)
	return		void
	param		plane		GLenum in value
	param		equation	ConstFixed in array [4]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Color3xOES(red, green, blue)
	return		void
	param		red		Fixed in value
	param		green		Fixed in value
	param		blue		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Color4xOES(red, green, blue, alpha)
	return		void
	param		red		Fixed in value
	param		green		Fixed in value
	param		blue		Fixed in value
	param		alpha		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Color3xvOES(components)
	return		void
	param		components	ConstFixed in array [3]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Color4xvOES(components)
	return		void
	param		components	ConstFixed in array [4]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ConvolutionParameterxOES(target, pname, param)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ConvolutionParameterxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DepthRangexOES(n, f)
	return		void
	param		n		ClampedFixed in value
	param		f		ClampedFixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EvalCoord1xOES(u)
	return		void
	param		u		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EvalCoord2xOES(u, v)
	return		void
	param		u		Fixed in value
	param		v		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EvalCoord1xvOES(coords)
	return		void
	param		coords		ConstFixed in array [1]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EvalCoord2xvOES(coords)
	return		void
	param		coords		ConstFixed in array [2]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FeedbackBufferxOES(n, type, buffer)
	return		void
	param		n		SizeI in value
	param		type		GLenum in value
	param		buffer		Fixed in array [n]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FogxOES(pname, param)
	return		void
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FogxvOES(pname, param)
	return		void
	param		pname		GLenum in value
	param		param		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FrustumxOES(l, r, b, t, n, f)
	return		void
	param		l		Fixed in value
	param		r		Fixed in value
	param		b		Fixed in value
	param		t		Fixed in value
	param		n		Fixed in value
	param		f		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetClipPlanexOES(plane, equation)
	return		void
	param		plane		GLenum in value
	param		equation	Fixed out array [4]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetConvolutionParameterxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetFixedvOES(pname, params)
	return		void
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetHistogramParameterxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetLightxOES(light, pname, params)
	return		void
	param		light		GLenum in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetMapxvOES(target, query, v)
	return		void
	param		target		GLenum in value
	param		query		GLenum in value
	param		v		Fixed out array [COMPSIZE(query)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetMaterialxOES(face, pname, param)
	return		void
	param		face		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetPixelMapxv(map, size, values)
	return		void
	param		map		GLenum in value
	param		size		Int32 in value
	param		values		Fixed out array [size]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetTexEnvxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetTexGenxvOES(coord, pname, params)
	return		void
	param		coord		GLenum in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetTexLevelParameterxvOES(target, level, pname, params)
	return		void
	param		target		GLenum in value
	param		level		Int32 in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetTexParameterxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		Fixed out array [COMPSIZE(pname)]
	category	OES_fixed_point
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

IndexxOES(component)
	return		void
	param		component	Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IndexxvOES(component)
	return		void
	param		component	ConstFixed in array [1]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LightModelxOES(pname, param)
	return		void
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LightModelxvOES(pname, param)
	return		void
	param		pname		GLenum in value
	param		param		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LightxOES(light, pname, param)
	return		void
	param		light		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LightxvOES(light, pname, params)
	return		void
	param		light		GLenum in value
	param		pname		GLenum in value
	param		params		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LineWidthxOES(width)
	return		void
	param		width		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LoadMatrixxOES(m)
	return		void
	param		m		ConstFixed in array [16]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

LoadTransposeMatrixxOES(m)
	return		void
	param		m		ConstFixed in array [16]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Map1xOES(target, u1, u2, stride, order, points)
	return		void
	param		target		GLenum in value
	param		u1		Fixed in value
	param		u2		Fixed in value
	param		stride		Int32 in value
	param		order		Int32 in value
	param		points		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Map2xOES(target, u1, u2, ustride, uorder, v1, v2, vstride, vorder, points)
	return		void
	param		target		GLenum in value
	param		u1		Fixed in value
	param		u2		Fixed in value
	param		ustride		Int32 in value
	param		uorder		Int32 in value
	param		v1		Fixed in value
	param		v2		Fixed in value
	param		vstride		Int32 in value
	param		vorder		Int32 in value
	param		points		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapGrid1xOES(n, u1, u2)
	return		void
	param		n		Int32 in value
	param		u1		Fixed in value
	param		u2		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapGrid2xOES(n, u1, u2, v1, v2)
	return		void
	param		n		Int32 in value
	param		u1		Fixed in value
	param		u2		Fixed in value
	param		v1		Fixed in value
	param		v2		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MaterialxOES(face, pname, param)
	return		void
	param		face		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MaterialxvOES(face, pname, param)
	return		void
	param		face		GLenum in value
	param		pname		GLenum in value
	param		param		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultMatrixxOES(m)
	return		void
	param		m		ConstFixed in array [16]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultTransposeMatrixxOES(m)
	return		void
	param		m		ConstFixed in array [16]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord1xOES(texture, s)
	return		void
	param		texture		GLenum in value
	param		s		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord2xOES(texture, s, t)
	return		void
	param		texture		GLenum in value
	param		s		Fixed in value
	param		t		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord3xOES(texture, s, t, r)
	return		void
	param		texture		GLenum in value
	param		s		Fixed in value
	param		t		Fixed in value
	param		r		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord4xOES(texture, s, t, r, q)
	return		void
	param		texture		GLenum in value
	param		s		Fixed in value
	param		t		Fixed in value
	param		r		Fixed in value
	param		q		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord1xvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstFixed in array [1]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord2xvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstFixed in array [2]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord3xvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstFixed in array [3]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiTexCoord4xvOES(texture, coords)
	return		void
	param		texture		GLenum in value
	param		coords		ConstFixed in array [4]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Normal3xOES(nx, ny, nz)
	return		void
	param		nx		Fixed in value
	param		ny		Fixed in value
	param		nz		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Normal3xvOES(coords)
	return		void
	param		coords		ConstFixed in array [3]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

OrthoxOES(l, r, b, t, n, f)
	return		void
	param		l		Fixed in value
	param		r		Fixed in value
	param		b		Fixed in value
	param		t		Fixed in value
	param		n		Fixed in value
	param		f		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PassThroughxOES(token)
	return		void
	param		token		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PixelMapx(map, size, values)
	return		void
	param		map		GLenum in value
	param		size		Int32 in value
	param		values		ConstFixed in array [size]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PixelStorex(pname, param)
	return		void
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PixelTransferxOES(pname, param)
	return		void
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PixelZoomxOES(xfactor, yfactor)
	return		void
	param		xfactor		Fixed in value
	param		yfactor		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PointParameterxvOES(pname, params)
	return		void
	param		pname		GLenum in value
	param		params		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PointSizexOES(size)
	return		void
	param		size		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PolygonOffsetxOES(factor, units)
	return		void
	param		factor		Fixed in value
	param		units		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PrioritizeTexturesxOES(n, textures, priorities)
	return		void
	param		n		SizeI in value
	param		textures	UInt32 in array [n]
	param		priorities	ClampedFixed in array [n]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RasterPos2xOES(x, y)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RasterPos3xOES(x, y, z)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	param		z		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RasterPos4xOES(x, y, z, w)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	param		z		Fixed in value
	param		w		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RasterPos2xvOES(coords)
	return		void
	param		coords		ConstFixed in array [2]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RasterPos3xvOES(coords)
	return		void
	param		coords		ConstFixed in array [3]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RasterPos4xvOES(coords)
	return		void
	param		coords		ConstFixed in array [4]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RectxOES(x1, y1, x2, y2)
	return		void
	param		x1		Fixed in value
	param		y1		Fixed in value
	param		x2		Fixed in value
	param		y2		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RectxvOES(v1, v2)
	return		void
	param		v1		ConstFixed in array [2]
	param		v2		ConstFixed in array [2]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

RotatexOES(angle, x, y, z)
	return		void
	param		angle		Fixed in value
	param		x		Fixed in value
	param		y		Fixed in value
	param		z		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SampleCoverageOES(value, invert)
	return		void
	param		value		ClampedFixed in value
	param		invert		Boolean in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ScalexOES(x, y, z)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	param		z		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord1xOES(s)
	return		void
	param		s		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord2xOES(s, t)
	return		void
	param		s		Fixed in value
	param		t		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord3xOES(s, t, r)
	return		void
	param		s		Fixed in value
	param		t		Fixed in value
	param		r		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord4xOES(s, t, r, q)
	return		void
	param		s		Fixed in value
	param		t		Fixed in value
	param		r		Fixed in value
	param		q		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord1xvOES(coords)
	return		void
	param		coords		ConstFixed in array [1]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord2xvOES(coords)
	return		void
	param		coords		ConstFixed in array [2]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord3xvOES(coords)
	return		void
	param		coords		ConstFixed in array [3]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoord4xvOES(coords)
	return		void
	param		coords		ConstFixed in array [4]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexEnvxOES(target, pname, param)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexEnvxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexGenxOES(coord, pname, param)
	return		void
	param		coord		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexGenxvOES(coord, pname, params)
	return		void
	param		coord		GLenum in value
	param		pname		GLenum in value
	param		params		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexParameterxOES(target, pname, param)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		param		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexParameterxvOES(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		ConstFixed in array [COMPSIZE(pname)]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TranslatexOES(x, y, z)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	param		z		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex2xOES(x)
	return		void
	param		x		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex3xOES(x, y)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex4xOES(x, y, z)
	return		void
	param		x		Fixed in value
	param		y		Fixed in value
	param		z		Fixed in value
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex2xvOES(coords)
	return		void
	param		coords		ConstFixed in array [2]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex3xvOES(coords)
	return		void
	param		coords		ConstFixed in array [3]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Vertex4xvOES(coords)
	return		void
	param		coords		ConstFixed in array [4]
	category	OES_fixed_point
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #293
# OES_single_precision commands
#
###############################################################################

DepthRangefOES(n, f)
	return		void
	param		n		ClampedFloat32 in value
	param		f		ClampedFloat32 in value
	category	OES_single_precision
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FrustumfOES(l, r, b, t, n, f)
	return		void
	param		l		Float32 in value
	param		r		Float32 in value
	param		b		Float32 in value
	param		t		Float32 in value
	param		n		Float32 in value
	param		f		Float32 in value
	category	OES_single_precision
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

OrthofOES(l, r, b, t, n, f)
	return		void
	param		l		Float32 in value
	param		r		Float32 in value
	param		b		Float32 in value
	param		t		Float32 in value
	param		n		Float32 in value
	param		f		Float32 in value
	category	OES_single_precision
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClipPlanefOES(plane, equation)
	return		void
	param		plane		GLenum in value
	param		equation	ConstFloat32 in array [4]
	category	OES_single_precision
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ClearDepthfOES(depth)
	return		void
	param		depth		ClampedFloat32 in value
	category	OES_single_precision
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetClipPlanefOES(plane, equation)
	return		void
	param		plane		GLenum in value
	param		equation	Float32 out array [4]
	category	OES_single_precision
	dlflags		notlistable
	version		4.3
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #294 - OpenGL ES only, not in glext.h
# OES_compressed_paletted_texture commands
#
###############################################################################

# (none)
newcategory: OES_compressed_paletted_texture

###############################################################################
#
# Extension #295
# OES_read_format commands
#
###############################################################################

# (none)
newcategory: OES_read_format

###############################################################################
#
# Extension #296
# OES_query_matrix commands
#
###############################################################################

QueryMatrixxOES(mantissa, exponent)
	return		GLbitfield
	param		mantissa	Fixed out array [16]
	param		exponent	Int32 out array [16]
	category	OES_query_matrix
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #297
# EXT_depth_bounds_test commands
#
###############################################################################

DepthBoundsEXT(zmin, zmax)
	return		void
	param		zmin		ClampedFloat64 in value
	param		zmax		ClampedFloat64 in value
	category	EXT_depth_bounds_test
	version		1.2
	extension
	glxropcode	4229
	offset		699

###############################################################################
#
# Extension #298
# EXT_texture_mirror_clamp commands
#
###############################################################################

# (none)
newcategory: EXT_texture_mirror_clamp

###############################################################################
#
# Extension #299
# EXT_blend_equation_separate commands
#
###############################################################################

BlendEquationSeparateEXT(modeRGB, modeAlpha)
	return		void
	param		modeRGB		BlendEquationModeEXT in value
	param		modeAlpha	BlendEquationModeEXT in value
	category	EXT_blend_equation_separate
	version		1.2
	extension
	glxropcode	4228
	alias		BlendEquationSeparate

###############################################################################
#
# Extension #300
# MESA_pack_invert commands
#
###############################################################################

# (none)
newcategory: MESA_pack_invert

###############################################################################
#
# Extension #301
# MESA_ycbcr_texture commands
#
###############################################################################

# (none)
newcategory: MESA_ycbcr_texture

###############################################################################
#
# Extension #301
# MESA_ycbcr_texture commands
#
###############################################################################

# (none)
newcategory: MESA_ycbcr_texture

###############################################################################
#
# Extension #302
# EXT_pixel_buffer_object commands
#
###############################################################################

# (none)
newcategory: EXT_pixel_buffer_object

###############################################################################
#
# Extension #303
# NV_fragment_program_option commands
#
###############################################################################

# (none)
newcategory: NV_fragment_program_option

###############################################################################
#
# Extension #304
# NV_fragment_program2 commands
#
###############################################################################

# (none)
newcategory: NV_fragment_program2

###############################################################################
#
# Extension #305
# NV_vertex_program2_option commands
#
###############################################################################

# (none)
newcategory: NV_vertex_program2_option

###############################################################################
#
# Extension #306
# NV_vertex_program3 commands
#
###############################################################################

# (none)
newcategory: NV_vertex_program3

###############################################################################
#
# Extension #307 - GLX_SGIX_hyperpipe commands
# Extension #308 - GLX_MESA_agp_offset commands
# Extension #309 - GL_EXT_texture_compression_dxt1 (OpenGL ES only, subset of _st3c version)
#
###############################################################################

# (none)
# newcategory: EXT_texture_compression_dxt1

###############################################################################
#
# Extension #310
# EXT_framebuffer_object commands
#
###############################################################################

IsRenderbufferEXT(renderbuffer)
	return		Boolean
	param		renderbuffer	UInt32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxvendorpriv	1422
	glxflags	ignore
	alias		IsRenderbuffer

# Not aliased to BindRenderbuffer
BindRenderbufferEXT(target, renderbuffer)
	return		void
	param		target		RenderbufferTarget in value
	param		renderbuffer	UInt32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4316
	glxflags	ignore

DeleteRenderbuffersEXT(n, renderbuffers)
	return		void
	param		n		SizeI in value
	param		renderbuffers	UInt32 in array [n]
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4317
	glxflags	ignore
	alias		DeleteRenderbuffers

GenRenderbuffersEXT(n, renderbuffers)
	return		void
	param		n		SizeI in value
	param		renderbuffers	UInt32 out array [n]
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxvendorpriv	1423
	glxflags	ignore
	alias		GenRenderbuffers

RenderbufferStorageEXT(target, internalformat, width, height)
	return		void
	param		target		RenderbufferTarget in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4318
	glxflags	ignore
	alias		RenderbufferStorage

GetRenderbufferParameterivEXT(target, pname, params)
	return		void
	param		target		RenderbufferTarget in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_framebuffer_object
	dlflags		notlistable
	version		1.2
	extension
	glxvendorpriv	1424
	glxflags	ignore
	alias		GetRenderbufferParameteriv

IsFramebufferEXT(framebuffer)
	return		Boolean
	param		framebuffer	UInt32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxvendorpriv	1425
	glxflags	ignore
	alias		IsFramebuffer

# Not aliased to BindFramebuffer
BindFramebufferEXT(target, framebuffer)
	return		void
	param		target		FramebufferTarget in value
	param		framebuffer	UInt32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4319
	glxflags	ignore

DeleteFramebuffersEXT(n, framebuffers)
	return		void
	param		n		SizeI in value
	param		framebuffers	UInt32 in array [n]
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4320
	glxflags	ignore
	alias		DeleteFramebuffers

GenFramebuffersEXT(n, framebuffers)
	return		void
	param		n		SizeI in value
	param		framebuffers	UInt32 out array [n]
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxvendorpriv	1426
	glxflags	ignore
	alias		GenFramebuffers

CheckFramebufferStatusEXT(target)
	return		GLenum
	param		target		FramebufferTarget in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxvendorpriv	1427
	glxflags	ignore
	alias		CheckFramebufferStatus

FramebufferTexture1DEXT(target, attachment, textarget, texture, level)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		textarget	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4321
	glxflags	ignore
	alias		FramebufferTexture1D

FramebufferTexture2DEXT(target, attachment, textarget, texture, level)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		textarget	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4322
	glxflags	ignore
	alias		FramebufferTexture2D

FramebufferTexture3DEXT(target, attachment, textarget, texture, level, zoffset)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		textarget	GLenum in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		zoffset		Int32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4323
	glxflags	ignore
	alias		FramebufferTexture3D

FramebufferRenderbufferEXT(target, attachment, renderbuffertarget, renderbuffer)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		renderbuffertarget	RenderbufferTarget in value
	param		renderbuffer	UInt32 in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4324
	glxflags	ignore
	alias		FramebufferRenderbuffer

GetFramebufferAttachmentParameterivEXT(target, attachment, pname, params)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_framebuffer_object
	dlflags		notlistable
	version		1.2
	extension
	glxvendorpriv	1428
	glxflags	ignore
	alias		GetFramebufferAttachmentParameteriv

GenerateMipmapEXT(target)
	return		void
	param		target		GLenum in value
	category	EXT_framebuffer_object
	version		1.2
	extension
	glxropcode	4325
	glxflags	ignore
	alias		GenerateMipmap


###############################################################################
#
# Extension #311
# GREMEDY_string_marker commands
#
###############################################################################

StringMarkerGREMEDY(len, string)
	return		void
	param		len		SizeI in value
	param		string		Void in array [len]
	category	GREMEDY_string_marker
	version		1.0
	extension
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #312
# EXT_packed_depth_stencil commands
#
###############################################################################

# (none)
newcategory: EXT_packed_depth_stencil

###############################################################################
#
# Extension #313 - WGL_3DL_stereo_control
#
###############################################################################

###############################################################################
#
# Extension #314
# EXT_stencil_clear_tag commands
#
###############################################################################

StencilClearTagEXT(stencilTagBits, stencilClearTag)
	return		void
	param		stencilTagBits	SizeI in value
	param		stencilClearTag UInt32 in value
	category	EXT_stencil_clear_tag
	version		1.5
	extension
	glxropcode	4223
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #315
# EXT_texture_sRGB commands
#
###############################################################################

# (none)
newcategory: EXT_texture_sRGB

###############################################################################
#
# Extension #316
# EXT_framebuffer_blit commands
#
###############################################################################

BlitFramebufferEXT(srcX0, srcY0, srcX1, srcY1, dstX0, dstY0, dstX1, dstY1, mask, filter)
	return		void
	param		srcX0		Int32 in value
	param		srcY0		Int32 in value
	param		srcX1		Int32 in value
	param		srcY1		Int32 in value
	param		dstX0		Int32 in value
	param		dstY0		Int32 in value
	param		dstX1		Int32 in value
	param		dstY1		Int32 in value
	param		mask		ClearBufferMask in value
	param		filter		GLenum in value
	category	EXT_framebuffer_blit
	version		1.5
	glxropcode	4330
	alias		BlitFramebuffer

###############################################################################
#
# Extension #317
# EXT_framebuffer_multisample commands
#
###############################################################################

RenderbufferStorageMultisampleEXT(target, samples, internalformat, width, height)
	return		void
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalformat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_framebuffer_multisample
	version		1.5
	glxropcode	4331
	alias		RenderbufferStorageMultisample

###############################################################################
#
# Extension #318
# MESAX_texture_stack commands
#
###############################################################################

# (none)
newcategory: MESAX_texture_stack

###############################################################################
#
# Extension #319
# EXT_timer_query commands
#
###############################################################################

GetQueryObjecti64vEXT(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		Int64EXT out array [pname]
	category	EXT_timer_query
	dlflags		notlistable
	version		1.5
	glxvendorpriv	1328
	glxflags	ignore
	offset		?

GetQueryObjectui64vEXT(id, pname, params)
	return		void
	param		id		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt64EXT out array [pname]
	category	EXT_timer_query
	dlflags		notlistable
	version		1.5
	glxvendorpriv	1329
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #320
# EXT_gpu_program_parameters commands
#
###############################################################################

ProgramEnvParameters4fvEXT(target, index, count, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		Float32 in array [count*4]
	category	EXT_gpu_program_parameters
	version		1.2
	glxropcode	4281
	offset		?

ProgramLocalParameters4fvEXT(target, index, count, params)
	return		void
	param		target		ProgramTargetARB in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		Float32 in array [count*4]
	category	EXT_gpu_program_parameters
	version		1.2
	glxropcode	4282
	offset		?

###############################################################################
#
# Extension #321
# APPLE_flush_buffer_range commands
#
###############################################################################

BufferParameteriAPPLE(target, pname, param)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		param		Int32 in value
	category	APPLE_flush_buffer_range
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FlushMappedBufferRangeAPPLE(target, offset, size)
	return		void
	param		target		GLenum in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	category	APPLE_flush_buffer_range
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	alias		FlushMappedBufferRange

###############################################################################
#
# Extension #322
# NV_gpu_program4 commands
#
###############################################################################

ProgramLocalParameterI4iNV(target, index, x, y, z, w)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	param		w		Int32 in value
	category	NV_gpu_program4
	version		1.3
	vectorequiv	ProgramLocalParameterI4ivNV
	glxvectorequiv	ProgramLocalParameterI4ivNV
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramLocalParameterI4ivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Int32 in array [4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramLocalParametersI4ivNV(target, index, count, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		Int32 in array [count*4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramLocalParameterI4uiNV(target, index, x, y, z, w)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	param		w		UInt32 in value
	category	NV_gpu_program4
	version		1.3
	vectorequiv	ProgramLocalParameterI4uivNV
	glxvectorequiv	ProgramLocalParameterI4uivNV
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramLocalParameterI4uivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		UInt32 in array [4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramLocalParametersI4uivNV(target, index, count, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		UInt32 in array [count*4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramEnvParameterI4iNV(target, index, x, y, z, w)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	param		w		Int32 in value
	category	NV_gpu_program4
	version		1.3
	vectorequiv	ProgramEnvParameterI4ivNV
	glxvectorequiv	ProgramEnvParameterI4ivNV
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramEnvParameterI4ivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Int32 in array [4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramEnvParametersI4ivNV(target, index, count, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		Int32 in array [count*4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramEnvParameterI4uiNV(target, index, x, y, z, w)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	param		w		UInt32 in value
	category	NV_gpu_program4
	version		1.3
	vectorequiv	ProgramEnvParameterI4uivNV
	glxvectorequiv	ProgramEnvParameterI4uivNV
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramEnvParameterI4uivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		UInt32 in array [4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramEnvParametersI4uivNV(target, index, count, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		UInt32 in array [count*4]
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

GetProgramLocalParameterIivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Int32 out array [4]
	dlflags		notlistable
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

GetProgramLocalParameterIuivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		UInt32 out array [4]
	dlflags		notlistable
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

GetProgramEnvParameterIivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Int32 out array [4]
	dlflags		notlistable
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

GetProgramEnvParameterIuivNV(target, index, params)
	return		void
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		UInt32 out array [4]
	dlflags		notlistable
	category	NV_gpu_program4
	version		1.3
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #323
# NV_geometry_program4 commands
#
###############################################################################

ProgramVertexLimitNV(target, limit)
	return		void
	param		target		ProgramTarget in value
	param		limit		Int32 in value
	category	NV_geometry_program4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore

FramebufferTextureEXT(target, attachment, texture, level)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	category	NV_geometry_program4
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	alias		FramebufferTextureARB

FramebufferTextureLayerEXT(target, attachment, texture, level, layer)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		layer		CheckedInt32 in value
	category	NV_geometry_program4
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	alias		FramebufferTextureLayer

FramebufferTextureFaceEXT(target, attachment, texture, level, face)
	return		void
	param		target		FramebufferTarget in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		face		TextureTarget in value
	category	NV_geometry_program4
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	alias		FramebufferTextureFaceARB

###############################################################################
#
# Extension #324
# EXT_geometry_shader4 commands
#
###############################################################################

ProgramParameteriEXT(program, pname, value)
	return		void
	param		program		UInt32 in value
	param		pname		ProgramParameterPName in value
	param		value		Int32 in value
	category	EXT_geometry_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		ProgramParameteriARB

###############################################################################
#
# Extension #325
# NV_vertex_program4 commands
#
###############################################################################

VertexAttribI1iEXT(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI1ivEXT
	glxvectorequiv	VertexAttribI1ivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI1i

VertexAttribI2iEXT(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI2ivEXT
	glxvectorequiv	VertexAttribI2ivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI2i

VertexAttribI3iEXT(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI3ivEXT
	glxvectorequiv	VertexAttribI3ivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI3i

VertexAttribI4iEXT(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	param		w		Int32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI4ivEXT
	glxvectorequiv	VertexAttribI4ivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4i

VertexAttribI1uiEXT(index, x)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI1uivEXT
	glxvectorequiv	VertexAttribI1uivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI1ui

VertexAttribI2uiEXT(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI2uivEXT
	glxvectorequiv	VertexAttribI2uivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI2ui

VertexAttribI3uiEXT(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI3uivEXT
	glxvectorequiv	VertexAttribI3uivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI3ui

VertexAttribI4uiEXT(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	param		w		UInt32 in value
	category	NV_vertex_program4
	beginend	allow-inside
	vectorequiv	VertexAttribI4uivEXT
	glxvectorequiv	VertexAttribI4uivEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4ui

VertexAttribI1ivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [1]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI1iv

VertexAttribI2ivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [2]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI2iv

VertexAttribI3ivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [3]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI3iv

VertexAttribI4ivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int32 in array [4]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4iv

VertexAttribI1uivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [1]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI1uiv

VertexAttribI2uivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [2]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI2uiv

VertexAttribI3uivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [3]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI3uiv

VertexAttribI4uivEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt32 in array [4]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4uiv

VertexAttribI4bvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int8 in array [4]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4bv

VertexAttribI4svEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int16 in array [4]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4sv

VertexAttribI4ubvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt8 in array [4]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4ubv

VertexAttribI4usvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt16 in array [4]
	category	NV_vertex_program4
	beginend	allow-inside
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribI4usv

VertexAttribIPointerEXT(index, size, type, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		VertexAttribEnum in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	NV_vertex_program4
	dlflags		notlistable
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		VertexAttribIPointer

GetVertexAttribIivEXT(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnum in value
	param		params		Int32 out array [1]
	category	NV_vertex_program4
	dlflags		notlistable
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		GetVertexAttribIiv

GetVertexAttribIuivEXT(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		VertexAttribEnum in value
	param		params		UInt32 out array [1]
	category	NV_vertex_program4
	dlflags		notlistable
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	alias		GetVertexAttribIuiv

###############################################################################
#
# Extension #326
# EXT_gpu_shader4 commands
#
###############################################################################

GetUniformuivEXT(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		UInt32 out array [COMPSIZE(program/location)]
	category	EXT_gpu_shader4
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		GetUniformuiv

BindFragDataLocationEXT(program, color, name)
	return		void
	param		program		UInt32 in value
	param		color		UInt32 in value
	param		name		Char in array [COMPSIZE(name)]
	category	EXT_gpu_shader4
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		BindFragDataLocation

GetFragDataLocationEXT(program, name)
	return		Int32
	param		program		UInt32 in value
	param		name		Char in array [COMPSIZE(name)]
	category	EXT_gpu_shader4
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		GetFragDataLocation

Uniform1uiEXT(location, v0)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform1ui

Uniform2uiEXT(location, v0, v1)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform2ui

Uniform3uiEXT(location, v0, v1, v2)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform3ui

Uniform4uiEXT(location, v0, v1, v2, v3)
	return		void
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	param		v3		UInt32 in value
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform4ui

Uniform1uivEXT(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count]
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform1uiv

Uniform2uivEXT(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*2]
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform2uiv

Uniform3uivEXT(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*3]
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform3uiv

Uniform4uivEXT(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*4]
	category	EXT_gpu_shader4
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		Uniform4uiv

###############################################################################
#
# Extension #327
# EXT_draw_instanced commands
#
###############################################################################

DrawArraysInstancedEXT(mode, start, count, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		start		Int32 in value
	param		count		SizeI in value
	param		primcount	SizeI in value
	category	EXT_draw_instanced
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	vectorequiv	ArrayElement
	glfflags	ignore
	glxflags	ignore
	alias		DrawArraysInstancedARB

DrawElementsInstancedEXT(mode, count, type, indices, primcount)
	return		void
	param		mode		PrimitiveType in value
	param		count		SizeI in value
	param		type		DrawElementsType in value
	param		indices		Void in array [COMPSIZE(count/type)]
	param		primcount	SizeI in value
	category	EXT_draw_instanced
	version		2.0
	extension	soft WINSOFT
	dlflags		notlistable
	vectorequiv	ArrayElement
	glfflags	ignore
	glxflags	ignore
	alias		DrawElementsInstancedARB

###############################################################################
#
# Extension #328
# EXT_packed_float commands
#
###############################################################################

# (none)
newcategory: EXT_packed_float

###############################################################################
#
# Extension #329
# EXT_texture_array commands
#
###############################################################################

# (none)
newcategory: EXT_texture_array

###############################################################################
#
# Extension #330
# EXT_texture_buffer_object commands
#
###############################################################################

TexBufferEXT(target, internalformat, buffer)
	return		void
	param		target		TextureTarget in value
	param		internalformat	GLenum in value
	param		buffer		UInt32 in value
	category	EXT_texture_buffer_object
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	alias		TexBufferARB

###############################################################################
#
# Extension #331
# EXT_texture_compression_latc commands
#
###############################################################################

# (none)
newcategory: EXT_texture_compression_latc

###############################################################################
#
# Extension #332
# EXT_texture_compression_rgtc commands
#
###############################################################################

# (none)
newcategory: EXT_texture_compression_rgtc

###############################################################################
#
# Extension #333
# EXT_texture_shared_exponent commands
#
###############################################################################

# (none)
newcategory: EXT_texture_shared_exponent

###############################################################################
#
# Extension #334
# NV_depth_buffer_float commands
#
###############################################################################

DepthRangedNV(zNear, zFar)
	return		void
	param		zNear		Float64 in value
	param		zFar		Float64 in value
	category	NV_depth_buffer_float
	extension	soft WINSOFT NV50
	version		2.0
	glfflags	ignore
	glxropcode	4283
	glxflags	ignore

ClearDepthdNV(depth)
	return		void
	param		depth		Float64 in value
	category	NV_depth_buffer_float
	extension	soft WINSOFT NV50
	version		2.0
	glfflags	ignore
	glxropcode	4284
	glxflags	ignore

DepthBoundsdNV(zmin, zmax)
	return		void
	param		zmin		Float64 in value
	param		zmax		Float64 in value
	category	NV_depth_buffer_float
	extension	soft WINSOFT NV50
	version		2.0
	glfflags	ignore
	glxropcode	4285
	glxflags	ignore

###############################################################################
#
# Extension #335
# NV_fragment_program4 commands
#
###############################################################################

# (none)
newcategory: NV_fragment_program4

###############################################################################
#
# Extension #336
# NV_framebuffer_multisample_coverage commands
#
###############################################################################

RenderbufferStorageMultisampleCoverageNV(target, coverageSamples, colorSamples, internalformat, width, height)
	return		void
	param		target		RenderbufferTarget in value
	param		coverageSamples SizeI in value
	param		colorSamples	SizeI in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	NV_framebuffer_multisample_coverage
	version		1.5
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #337
# EXT_framebuffer_sRGB commands
#
###############################################################################

# (none)
newcategory: EXT_framebuffer_sRGB

###############################################################################
#
# Extension #338
# NV_geometry_shader4 commands
#
###############################################################################

# (none)
newcategory: NV_geometry_shader4

###############################################################################
#
# Extension #339
# NV_parameter_buffer_object commands
#
###############################################################################

ProgramBufferParametersfvNV(target, bindingIndex, wordIndex, count, params)
	return		void
	param		target		ProgramTarget in value
	param		bindingIndex	UInt32 in value
	param		wordIndex	UInt32 in value
	param		count		SizeI in value
	param		params		Float32 in array [count]
	category	NV_parameter_buffer_object
	version		1.2
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramBufferParametersIivNV(target, bindingIndex, wordIndex, count, params)
	return		void
	param		target		ProgramTarget in value
	param		bindingIndex	UInt32 in value
	param		wordIndex	UInt32 in value
	param		count		SizeI in value
	param		params		Int32 in array [count]
	category	NV_parameter_buffer_object
	version		1.2
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ProgramBufferParametersIuivNV(target, bindingIndex, wordIndex, count, params)
	return		void
	param		target		ProgramTarget in value
	param		bindingIndex	UInt32 in value
	param		wordIndex	UInt32 in value
	param		count		SizeI in value
	param		params		UInt32 in array [count]
	category	NV_parameter_buffer_object
	version		1.2
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #340
# EXT_draw_buffers2 commands
#
###############################################################################

ColorMaskIndexedEXT(index, r, g, b, a)
	return		void
	param		index		UInt32 in value
	param		r		Boolean in value
	param		g		Boolean in value
	param		b		Boolean in value
	param		a		Boolean in value
	category	EXT_draw_buffers2
	version		2.0
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		ColorMaski

GetBooleanIndexedvEXT(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Boolean out array [COMPSIZE(target)]
	category	EXT_draw_buffers2
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		GetBooleani_v

GetIntegerIndexedvEXT(target, index, data)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		data		Int32 out array [COMPSIZE(target)]
	category	EXT_draw_buffers2
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		GetIntegeri_v

EnableIndexedEXT(target, index)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	category	EXT_draw_buffers2
	version		2.0
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		Enablei

DisableIndexedEXT(target, index)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	category	EXT_draw_buffers2
	version		2.0
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		Disablei

IsEnabledIndexedEXT(target, index)
	return		Boolean
	param		target		GLenum in value
	param		index		UInt32 in value
	category	EXT_draw_buffers2
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		IsEnabledi

###############################################################################
#
# Extension #341
# NV_transform_feedback commands
#
###############################################################################

BeginTransformFeedbackNV(primitiveMode)
	return		void
	param		primitiveMode	GLenum in value
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BeginTransformFeedback

EndTransformFeedbackNV()
	return		void
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		EndTransformFeedback

TransformFeedbackAttribsNV(count, attribs, bufferMode)
	return		void
	param		count		UInt32 in value
	param		attribs		Int32 in array [COMPSIZE(count)]
	param		bufferMode	GLenum in value
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT

BindBufferRangeNV(target, index, buffer, offset, size)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BindBufferRange

BindBufferOffsetNV(target, index, buffer, offset)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BindBufferOffsetEXT

BindBufferBaseNV(target, index, buffer)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BindBufferBase

TransformFeedbackVaryingsNV(program, count, locations, bufferMode)
	return		void
	param		program		UInt32 in value
	param		count		SizeI in value
	param		locations	Int32 in array [count]
	param		bufferMode	GLenum in value
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		TransformFeedbackVaryings

ActiveVaryingNV(program, name)
	return		void
	param		program		UInt32 in value
	param		name		Char in array [COMPSIZE(name)]
	category	NV_transform_feedback
	version		1.5
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT

GetVaryingLocationNV(program, name)
	return		Int32
	param		program		UInt32 in value
	param		name		Char in array [COMPSIZE(name)]
	category	NV_transform_feedback
	dlflags		notlistable
	version		1.5
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT

GetActiveVaryingNV(program, index, bufSize, length, size, type, name)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		size		SizeI out array [1]
	param		type		GLenum out array [1]
	param		name		Char out array [COMPSIZE(program/index/bufSize)]
	category	NV_transform_feedback
	dlflags		notlistable
	version		1.5
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore

GetTransformFeedbackVaryingNV(program, index, location)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		location	Int32 out array [1]
	category	NV_transform_feedback
	dlflags		notlistable
	version		1.5
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		GetTransformFeedbackVarying

# These commands require ARB_transform_feedback3

TransformFeedbackStreamAttribsNV(count, attribs, nbuffers, bufstreams, bufferMode)
	return		void
	param		count		SizeI in value
	param		attribs		Int32 in array [count]
	param		nbuffers	SizeI in value
	param		bufstreams	Int32 in array [nbuffers]
	param		bufferMode	GLenum in value
	category	NV_transform_feedback
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?


###############################################################################
#
# Extension #342
# EXT_bindable_uniform commands
#
###############################################################################

UniformBufferEXT(program, location, buffer)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		buffer		UInt32 in value
	category	EXT_bindable_uniform
	version		2.0
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

GetUniformBufferSizeEXT(program, location)
	return		Int32
	param		program		UInt32 in value
	param		location	Int32 in value
	category	EXT_bindable_uniform
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore

GetUniformOffsetEXT(program, location)
	return		BufferOffset
	param		program		UInt32 in value
	param		location	Int32 in value
	category	EXT_bindable_uniform
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #343
# EXT_texture_integer extension commands
#
###############################################################################

TexParameterIivEXT(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	EXT_texture_integer
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	alias		TexParameterIiv

TexParameterIuivEXT(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		UInt32 in array [COMPSIZE(pname)]
	category	EXT_texture_integer
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	alias		TexParameterIuiv

GetTexParameterIivEXT(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_texture_integer
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	alias		GetTexParameterIiv

GetTexParameterIuivEXT(target, pname, params)
	return		void
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	category	EXT_texture_integer
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	alias		GetTexParameterIuiv

ClearColorIiEXT(red, green, blue, alpha)
	return		void
	param		red		Int32 in value
	param		green		Int32 in value
	param		blue		Int32 in value
	param		alpha		Int32 in value
	category	EXT_texture_integer
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

ClearColorIuiEXT(red, green, blue, alpha)
	return		void
	param		red		UInt32 in value
	param		green		UInt32 in value
	param		blue		UInt32 in value
	param		alpha		UInt32 in value
	category	EXT_texture_integer
	version		2.0
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #344 - GLX_EXT_texture_from_pixmap
#
###############################################################################

###############################################################################
#
# Extension #345
# GREMEDY_frame_terminator commands
#
###############################################################################

FrameTerminatorGREMEDY()
	return		void
	category	GREMEDY_frame_terminator
	version		1.0
	extension
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #346
# NV_conditional_render commands
#
###############################################################################

BeginConditionalRenderNV(id, mode)
	return		void
	param		id		UInt32 in value
	param		mode		TypeEnum in value
	category	NV_conditional_render
	glfflags	ignore
	glxflags	ignore
	alias		BeginConditionalRender

EndConditionalRenderNV()
	return		void
	category	NV_conditional_render
	glfflags	ignore
	glxflags	ignore
	alias		EndConditionalRender

###############################################################################
#
# Extension #347
# NV_present_video commands
#
###############################################################################

PresentFrameKeyedNV(video_slot, minPresentTime, beginPresentTimeId, presentDurationId, type, target0, fill0, key0, target1, fill1, key1)
	return		void
	param		video_slot	UInt32 in value
	param		minPresentTime	UInt64EXT in value
	param		beginPresentTimeId	UInt32 in value
	param		presentDurationId	UInt32 in value
	param		type		GLenum in value
	param		target0		GLenum in value
	param		fill0		UInt32 in value
	param		key0		UInt32 in value
	param		target1		GLenum in value
	param		fill1		UInt32 in value
	param		key1		UInt32 in value
	category	NV_present_video
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

PresentFrameDualFillNV(video_slot, minPresentTime, beginPresentTimeId, presentDurationId, type, target0, fill0, target1, fill1, target2, fill2, target3, fill3)
	return		void
	param		video_slot	UInt32 in value
	param		minPresentTime	UInt64EXT in value
	param		beginPresentTimeId	UInt32 in value
	param		presentDurationId	UInt32 in value
	param		type		GLenum in value
	param		target0		GLenum in value
	param		fill0		UInt32 in value
	param		target1		GLenum in value
	param		fill1		UInt32 in value
	param		target2		GLenum in value
	param		fill2		UInt32 in value
	param		target3		GLenum in value
	param		fill3		UInt32 in value
	category	NV_present_video
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVideoivNV(video_slot, pname, params)
	return		void
	param		video_slot	UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	NV_present_video
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVideouivNV(video_slot, pname, params)
	return		void
	param		video_slot	UInt32 in value
	param		pname		GLenum in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	category	NV_present_video
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVideoi64vNV(video_slot, pname, params)
	return		void
	param		video_slot	UInt32 in value
	param		pname		GLenum in value
	param		params		Int64EXT out array [COMPSIZE(pname)]
	category	NV_present_video
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVideoui64vNV(video_slot, pname, params)
	return		void
	param		video_slot	UInt32 in value
	param		pname		GLenum in value
	param		params		UInt64EXT out array [COMPSIZE(pname)]
	category	NV_present_video
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #348 - GLX_NV_video_out
# Extension #349 - WGL_NV_video_out
# Extension #350 - GLX_NV_swap_group
# Extension #351 - WGL_NV_swap_group
#
###############################################################################

###############################################################################
#
# Extension #352
# EXT_transform_feedback commands
#
###############################################################################

# From EXT_draw_buffers2:  GetBooleanIndexedvEXT / GetIntegerIndexedvEXT

BeginTransformFeedbackEXT(primitiveMode)
	return		void
	param		primitiveMode	GLenum in value
	category	EXT_transform_feedback
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BeginTransformFeedback

EndTransformFeedbackEXT()
	return		void
	category	EXT_transform_feedback
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		EndTransformFeedback

BindBufferRangeEXT(target, index, buffer, offset, size)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	param		size		BufferSize in value
	category	EXT_transform_feedback
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BindBufferRange

# Not promoted to the OpenGL 3.0 core
BindBufferOffsetEXT(target, index, buffer, offset)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	param		offset		BufferOffset in value
	category	EXT_transform_feedback
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT

BindBufferBaseEXT(target, index, buffer)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		buffer		UInt32 in value
	category	EXT_transform_feedback
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		BindBufferBase

TransformFeedbackVaryingsEXT(program, count, varyings, bufferMode)
	return		void
	param		program		UInt32 in value
	param		count		SizeI in value
	param		varyings	CharPointer in array [count]
	param		bufferMode	GLenum in value
	category	EXT_transform_feedback
	version		2.0
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT
	alias		TransformFeedbackVaryings

GetTransformFeedbackVaryingEXT(program, index, bufSize, length, size, type, name)
	return		void
	param		program		UInt32 in value
	param		index		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		size		SizeI out array [1]
	param		type		GLenum out array [1]
	param		name		Char out array [COMPSIZE(length)]
	category	EXT_transform_feedback
	dlflags		notlistable
	version		2.0
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	alias		GetTransformFeedbackVarying

###############################################################################
#
# Extension #353
# EXT_direct_state_access commands
#
###############################################################################

# New 1.1 client commands

ClientAttribDefaultEXT(mask)
	return		void
	param		mask		ClientAttribMask in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore ### client-handcode client-intercept server-handcode

PushClientAttribDefaultEXT(mask)
	return		void
	param		mask		ClientAttribMask in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore ### client-handcode client-intercept server-handcode

# New 1.0 matrix commands

MatrixLoadfEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float32 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixLoaddEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float64 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixMultfEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float32 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixMultdEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float64 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixLoadIdentityEXT(mode)
	return		void
	param		mode		MatrixMode in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixRotatefEXT(mode, angle, x, y, z)
	return		void
	param		mode		MatrixMode in value
	param		angle		Float32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixRotatedEXT(mode, angle, x, y, z)
	return		void
	param		mode		MatrixMode in value
	param		angle		Float64 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixScalefEXT(mode, x, y, z)
	return		void
	param		mode		MatrixMode in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixScaledEXT(mode, x, y, z)
	return		void
	param		mode		MatrixMode in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixTranslatefEXT(mode, x, y, z)
	return		void
	param		mode		MatrixMode in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixTranslatedEXT(mode, x, y, z)
	return		void
	param		mode		MatrixMode in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixFrustumEXT(mode, left, right, bottom, top, zNear, zFar)
	return		void
	param		mode		MatrixMode in value
	param		left		Float64 in value
	param		right		Float64 in value
	param		bottom		Float64 in value
	param		top		Float64 in value
	param		zNear		Float64 in value
	param		zFar		Float64 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixOrthoEXT(mode, left, right, bottom, top, zNear, zFar)
	return		void
	param		mode		MatrixMode in value
	param		left		Float64 in value
	param		right		Float64 in value
	param		bottom		Float64 in value
	param		top		Float64 in value
	param		zNear		Float64 in value
	param		zFar		Float64 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixPopEXT(mode)
	return		void
	param		mode		MatrixMode in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixPushEXT(mode)
	return		void
	param		mode		MatrixMode in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

# New 1.3 matrix transpose commands

MatrixLoadTransposefEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float32 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixLoadTransposedEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float64 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixMultTransposefEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float32 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MatrixMultTransposedEXT(mode, m)
	return		void
	param		mode		MatrixMode in value
	param		m		Float64 in array [16]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

# New 1.1 texture object commands

TextureParameterfEXT(texture, target, pname, param)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		param		CheckedFloat32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	vectorequiv	TextureParameterfvEXT

TextureParameterfvEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

TextureParameteriEXT(texture, target, pname, param)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		param		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	vectorequiv	TextureParameterivEXT

TextureParameterivEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

TextureImage1DEXT(texture, target, level, internalformat, width, border, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	capture-handcode decode-handcode pixel-unpack

TextureImage2DEXT(texture, target, level, internalformat, width, height, border, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	capture-handcode decode-handcode pixel-unpack

TextureSubImage1DEXT(texture, target, level, xoffset, width, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### EXT client-handcode server-handcode
	glxflags	ignore
	extension	soft WINSOFT
	glfflags	ignore

TextureSubImage2DEXT(texture, target, level, xoffset, yoffset, width, height, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### EXT client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	ignore

CopyTextureImage1DEXT(texture, target, level, internalformat, x, y, width, border)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

CopyTextureImage2DEXT(texture, target, level, internalformat, x, y, width, height, border)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

CopyTextureSubImage1DEXT(texture, target, level, xoffset, x, y, width)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

CopyTextureSubImage2DEXT(texture, target, level, xoffset, yoffset, x, y, width, height)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

# New 1.1 texture object queries

GetTextureImageEXT(texture, target, level, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void out array [COMPSIZE(target/level/format/type)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore ### client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	capture-execute capture-handcode decode-handcode pixel-pack

GetTextureParameterfvEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetTextureParameterivEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetTextureLevelParameterfvEXT(texture, target, level, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		pname		GetTextureParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetTextureLevelParameterivEXT(texture, target, level, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

# New 1.2 3D texture object commands

TextureImage3DEXT(texture, target, level, internalformat, width, height, depth, border, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode EXT
	extension	soft WINSOFT
	glfflags	ignore

TextureSubImage3DEXT(texture, target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode EXT
	extension	soft WINSOFT
	glfflags	ignore

CopyTextureSubImage3DEXT(texture, target, level, xoffset, yoffset, zoffset, x, y, width, height)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	glxflags	ignore ### EXT
	extension	soft WINSOFT
	glfflags	ignore

# New 1.1 multitexture commands

MultiTexParameterfEXT(texunit, target, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		param		CheckedFloat32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	vectorequiv	MultiTexParameterfvEXT

MultiTexParameterfvEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MultiTexParameteriEXT(texunit, target, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		param		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	vectorequiv	MultiTexParameterivEXT

MultiTexParameterivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore

MultiTexImage1DEXT(texunit, target, level, internalformat, width, border, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	capture-handcode decode-handcode pixel-unpack

MultiTexImage2DEXT(texunit, target, level, internalformat, width, height, border, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	capture-handcode decode-handcode pixel-unpack

MultiTexSubImage1DEXT(texunit, target, level, xoffset, width, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### EXT client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	ignore

MultiTexSubImage2DEXT(texunit, target, level, xoffset, yoffset, width, height, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### EXT client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	ignore

CopyMultiTexImage1DEXT(texunit, target, level, internalformat, x, y, width, border)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

CopyMultiTexImage2DEXT(texunit, target, level, internalformat, x, y, width, height, border)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

CopyMultiTexSubImage1DEXT(texunit, target, level, xoffset, x, y, width)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

CopyMultiTexSubImage2DEXT(texunit, target, level, xoffset, yoffset, x, y, width, height)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

# New 1.1 multitexture queries

GetMultiTexImageEXT(texunit, target, level, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void out array [COMPSIZE(target/level/format/type)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore ### client-handcode server-handcode
	extension	soft WINSOFT
	glfflags	capture-execute capture-handcode decode-handcode pixel-pack

GetMultiTexParameterfvEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexParameterivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexLevelParameterfvEXT(texunit, target, level, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		pname		GetTextureParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexLevelParameterivEXT(texunit, target, level, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

# New 1.2 3D multitexture commands

MultiTexImage3DEXT(texunit, target, level, internalformat, width, height, depth, border, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode EXT
	extension	soft WINSOFT
	glfflags	ignore

MultiTexSubImage3DEXT(texunit, target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		type		PixelType in value
	param		pixels		Void in array [COMPSIZE(format/type/width/height/depth)]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode EXT
	extension	soft WINSOFT
	glfflags	ignore

CopyMultiTexSubImage3DEXT(texunit, target, level, xoffset, yoffset, zoffset, x, y, width, height)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		x		WinCoord in value
	param		y		WinCoord in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	glxflags	ignore ### EXT
	extension	soft WINSOFT
	glfflags	ignore

# New 1.2.1 multitexture texture commands

BindMultiTextureEXT(texunit, target, texture)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		texture		Texture in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore ### EXT

EnableClientStateIndexedEXT(array, index)
	return		void
	param		array		EnableCap in value
	param		index		UInt32 in value
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore ### client-handcode client-intercept server-handcode
	extension	soft WINSOFT

DisableClientStateIndexedEXT(array, index)
	return		void
	param		array		EnableCap in value
	param		index		UInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore ### client-handcode client-intercept server-handcode

MultiTexCoordPointerEXT(texunit, size, type, stride, pointer)
	return		void
	param		texunit		TextureUnit in value
	param		size		Int32 in value
	param		type		TexCoordPointerType in value
	param		stride		SizeI in value
	param		pointer		Void in array [COMPSIZE(size/type/stride)] retained
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore ### client-handcode client-intercept server-handcode
	extension	soft WINSOFT
	glfflags	ignore

MultiTexEnvfEXT(texunit, target, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		param		CheckedFloat32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	vectorequiv	MultiTexEnvfvEXT
	glxflags	ignore
	glfflags	gl-enum

MultiTexEnvfvEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	gl-enum

MultiTexEnviEXT(texunit, target, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		param		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	vectorequiv	MultiTexEnvivEXT
	glxflags	ignore
	glfflags	gl-enum

MultiTexEnvivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	gl-enum

MultiTexGendEXT(texunit, coord, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		param		Float64 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	vectorequiv	MultiTexGendvEXT
	glxflags	ignore
	glfflags	gl-enum

MultiTexGendvEXT(texunit, coord, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Float64 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	gl-enum

MultiTexGenfEXT(texunit, coord, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		param		CheckedFloat32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	vectorequiv	MultiTexGenfvEXT
	glxflags	ignore
	glfflags	gl-enum

MultiTexGenfvEXT(texunit, coord, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		CheckedFloat32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	gl-enum

MultiTexGeniEXT(texunit, coord, pname, param)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		param		CheckedInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	vectorequiv	MultiTexGenivEXT
	glxflags	ignore
	glfflags	gl-enum

MultiTexGenivEXT(texunit, coord, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	gl-enum

# New 1.2.1 multitexture texture queries

GetMultiTexEnvfvEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexEnvivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureEnvTarget in value
	param		pname		TextureEnvParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexGendvEXT(texunit, coord, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Float64 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexGenfvEXT(texunit, coord, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

GetMultiTexGenivEXT(texunit, coord, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		coord		TextureCoordName in value
	param		pname		TextureGenParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

# From EXT_draw_buffers2
# EnableIndexedEXT
# DisableIndexedEXT
# IsEnabledIndexedEXT

GetFloatIndexedvEXT(target, index, data)
	return		void
	param		target		TypeEnum in value
	param		index		UInt32 in value
	param		data		Float32 out array [COMPSIZE(target)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT

GetDoubleIndexedvEXT(target, index, data)
	return		void
	param		target		TypeEnum in value
	param		index		UInt32 in value
	param		data		Float64 out array [COMPSIZE(target)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT

GetPointerIndexedvEXT(target, index, data)
	return		void
	param		target		TypeEnum in value
	param		index		UInt32 in value
	param		data		VoidPointer out array [COMPSIZE(target)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore
	extension	soft WINSOFT

# New compressed texture commands

CompressedTextureImage3DEXT(texture, target, level, internalformat, width, height, depth, border, imageSize, bits)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedTextureImage2DEXT(texture, target, level, internalformat, width, height, border, imageSize, bits)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedTextureImage1DEXT(texture, target, level, internalformat, width, border, imageSize, bits)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedTextureSubImage3DEXT(texture, target, level, xoffset, yoffset, zoffset, width, height, depth, format, imageSize, bits)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedTextureSubImage2DEXT(texture, target, level, xoffset, yoffset, width, height, format, imageSize, bits)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedTextureSubImage1DEXT(texture, target, level, xoffset, width, format, imageSize, bits)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

# New compressed texture query

GetCompressedTextureImageEXT(texture, target, lod, img)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		lod		CheckedInt32 in value
	param		img		Void out array [COMPSIZE(target/lod)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore ### server-handcode
	extension	soft WINSOFT

# New compressed multitexture commands

CompressedMultiTexImage3DEXT(texunit, target, level, internalformat, width, height, depth, border, imageSize, bits)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedMultiTexImage2DEXT(texunit, target, level, internalformat, width, height, border, imageSize, bits)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedMultiTexImage1DEXT(texunit, target, level, internalformat, width, border, imageSize, bits)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		internalformat	TextureInternalFormat in value
	param		width		SizeI in value
	param		border		CheckedInt32 in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedMultiTexSubImage3DEXT(texunit, target, level, xoffset, yoffset, zoffset, width, height, depth, format, imageSize, bits)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedMultiTexSubImage2DEXT(texunit, target, level, xoffset, yoffset, width, height, format, imageSize, bits)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		yoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

CompressedMultiTexSubImage1DEXT(texunit, target, level, xoffset, width, format, imageSize, bits)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		level		CheckedInt32 in value
	param		xoffset		CheckedInt32 in value
	param		width		SizeI in value
	param		format		PixelFormat in value
	param		imageSize	SizeI in value
	param		bits		Void in array [imageSize]
	category	EXT_direct_state_access
	dlflags		handcode
	glxflags	ignore ### client-handcode server-handcode
	glfflags	ignore
	extension	soft WINSOFT

# New compressed multitexture query

GetCompressedMultiTexImageEXT(texunit, target, lod, img)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		lod		CheckedInt32 in value
	param		img		Void out array [COMPSIZE(target/lod)]
	category	EXT_direct_state_access
	dlflags		notlistable
	glxflags	ignore ### server-handcode
	extension	soft WINSOFT

# New ARB assembly program named commands

NamedProgramStringEXT(program, target, format, len, string)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		format		ProgramFormat in value
	param		len		SizeI in value
	param		string		Void in array [len]
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore ### client-handcode server-handcode EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

NamedProgramLocalParameter4dEXT(program, target, index, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	vectorequiv	NamedProgramLocalParameter4dvEXT
	glxvectorequiv	NamedProgramLocalParameter4dvEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

NamedProgramLocalParameter4dvEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Float64 in array [4]
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

NamedProgramLocalParameter4fEXT(program, target, index, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		Float32 in value
	param		y		Float32 in value
	param		z		Float32 in value
	param		w		Float32 in value
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	vectorequiv	NamedProgramLocalParameter4fvEXT
	glxvectorequiv	NamedProgramLocalParameter4fvEXT
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

NamedProgramLocalParameter4fvEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Float32 in array [4]
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

# New ARB assembly program named queries

GetNamedProgramLocalParameterdvEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Float64 out array [4]
	dlflags		notlistable
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### client-handcode server-handcode EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

GetNamedProgramLocalParameterfvEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Float32 out array [4]
	dlflags		notlistable
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### client-handcode server-handcode EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

GetNamedProgramivEXT(program, target, pname, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		pname		ProgramProperty in value
	param		params		Int32 out array [1]
	dlflags		notlistable
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### client-handcode server-handcode EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

GetNamedProgramStringEXT(program, target, pname, string)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		pname		ProgramStringProperty in value
	param		string		Void out array [COMPSIZE(program,pname)]
	dlflags		notlistable
	category	EXT_direct_state_access
	subcategory	ARB_vertex_program
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore ### client-handcode server-handcode EXT
	glextmask	GL_MASK_ARB_vertex_program|GL_MASK_ARB_fragment_program

# New EXT_gpu_program_parameters command

NamedProgramLocalParameters4fvEXT(program, target, index, count, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		Float32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	EXT_gpu_program_parameters
	extension	soft WINSOFT NV10
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_gpu_program_parameters

# New NV_gpu_program4 commands

NamedProgramLocalParameterI4iEXT(program, target, index, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		Int32 in value
	param		y		Int32 in value
	param		z		Int32 in value
	param		w		Int32 in value
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	vectorequiv	NamedProgramLocalParameterI4ivEXT
	glxvectorequiv	NamedProgramLocalParameterI4ivEXT
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedProgramLocalParameterI4ivEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Int32 in array [4]
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedProgramLocalParametersI4ivEXT(program, target, index, count, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		Int32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedProgramLocalParameterI4uiEXT(program, target, index, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		x		UInt32 in value
	param		y		UInt32 in value
	param		z		UInt32 in value
	param		w		UInt32 in value
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	vectorequiv	NamedProgramLocalParameterI4uivEXT
	glxvectorequiv	NamedProgramLocalParameterI4uivEXT
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedProgramLocalParameterI4uivEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		UInt32 in array [4]
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedProgramLocalParametersI4uivEXT(program, target, index, count, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		count		SizeI in value
	param		params		UInt32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

GetNamedProgramLocalParameterIivEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		Int32 out array [4]
	dlflags		notlistable
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

GetNamedProgramLocalParameterIuivEXT(program, target, index, params)
	return		void
	param		program		UInt32 in value
	param		target		ProgramTarget in value
	param		index		UInt32 in value
	param		params		UInt32 out array [4]
	dlflags		notlistable
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

# New EXT_texture_integer texture object commands

TextureParameterIivEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	glextmask	GL_MASK_EXT_texture_integer

TextureParameterIuivEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		UInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	glextmask	GL_MASK_EXT_texture_integer

# New EXT_texture_integer texture object queries

GetTextureParameterIivEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum
	glextmask	GL_MASK_EXT_texture_integer

GetTextureParameterIuivEXT(texture, target, pname, params)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum
	glextmask	GL_MASK_EXT_texture_integer

# New EXT_texture_integer multitexture commands

MultiTexParameterIivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		CheckedInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	glextmask	GL_MASK_EXT_texture_integer

MultiTexParameterIuivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		TextureParameterName in value
	param		params		UInt32 in array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	ignore
	glextmask	GL_MASK_EXT_texture_integer

# New EXT_texture_integer multitexture queries

GetMultiTexParameterIivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	dlflags		notlistable
	extension	soft WINSOFT
	glfflags	capture-execute gl-enum
	glxflags	ignore
	glextmask	GL_MASK_EXT_texture_integer

GetMultiTexParameterIuivEXT(texunit, target, pname, params)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		pname		GetTextureParameter in value
	param		params		UInt32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_texture_integer
	dlflags		notlistable
	extension	soft WINSOFT
	glfflags	capture-execute gl-enum
	glxflags	ignore
	glextmask	GL_MASK_EXT_texture_integer

# New GLSL 2.0 uniform commands

ProgramUniform1fEXT(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform2fEXT(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform3fEXT(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform4fEXT(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Float32 in value
	param		v1		Float32 in value
	param		v2		Float32 in value
	param		v3		Float32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform1iEXT(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform2iEXT(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform3iEXT(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform4iEXT(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		Int32 in value
	param		v1		Int32 in value
	param		v2		Int32 in value
	param		v3		Int32 in value
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform1fvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform2fvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count*2]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform3fvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count*3]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform4fvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform1ivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform2ivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count*2]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform3ivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count*3]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform4ivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix2fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix3fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*9]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix4fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*16]
	category	EXT_direct_state_access
	subcategory	VERSION_2_0
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

# New GLSL 2.1 uniform commands

ProgramUniformMatrix2x3fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*6]
	category	EXT_direct_state_access
	subcategory	VERSION_2_1
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix3x2fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*6]
	category	EXT_direct_state_access
	subcategory	VERSION_2_1
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix2x4fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*8]
	category	EXT_direct_state_access
	subcategory	VERSION_2_1
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix4x2fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*8]
	category	EXT_direct_state_access
	subcategory	VERSION_2_1
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix3x4fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*12]
	category	EXT_direct_state_access
	subcategory	VERSION_2_1
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniformMatrix4x3fvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float32 in array [count*12]
	category	EXT_direct_state_access
	subcategory	VERSION_2_1
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

# New EXT_gpu_shader4 commands

ProgramUniform1uiEXT(program, location, v0)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform2uiEXT(program, location, v0, v1)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform3uiEXT(program, location, v0, v1, v2)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform4uiEXT(program, location, v0, v1, v2, v3)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		v0		UInt32 in value
	param		v1		UInt32 in value
	param		v2		UInt32 in value
	param		v3		UInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform1uivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count]
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform2uivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*2]
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform3uivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*3]
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

ProgramUniform4uivEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt32 in array [count*4]
	category	EXT_direct_state_access
	subcategory	EXT_gpu_shader4
	glfflags	ignore
	glxflags	ignore
	extension	soft WINSOFT
	glextmask	GL_MASK_OpenGL_2_0

# New named buffer commands

NamedBufferDataEXT(buffer, size, data, usage)
	return		void
	param		buffer		UInt32 in value
	param		size		Sizeiptr in value
	param		data		Void in array [COMPSIZE(size)]
	param		usage		VertexBufferObjectUsage in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

NamedBufferSubDataEXT(buffer, offset, size, data)
	return		void
	param		buffer		UInt32 in value
	param		offset		Intptr in value
	param		size		Sizeiptr in value
	param		data		Void in array [COMPSIZE(size)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

MapNamedBufferEXT(buffer, access)
	return		VoidPointer
	param		buffer		UInt32 in value
	param		access		VertexBufferObjectAccess in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

UnmapNamedBufferEXT(buffer)
	return		Boolean
	param		buffer		UInt32 in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

MapNamedBufferRangeEXT(buffer, offset, length, access)
	return		VoidPointer
	param		buffer		UInt32 in value
	param		offset		Intptr in value
	param		length		Sizeiptr in value
	param		access		BufferAccessMask in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

FlushMappedNamedBufferRangeEXT(buffer, offset, length)
	return		void
	param		buffer		UInt32 in value
	param		offset		Intptr in value
	param		length		Sizeiptr in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

NamedCopyBufferSubDataEXT(readBuffer, writeBuffer, readOffset, writeOffset, size)
	return		void
	param		readBuffer	UInt32 in value
	param		writeBuffer	UInt32 in value
	param		readOffset	Intptr in value
	param		writeOffset	Intptr in value
	param		size		Sizeiptr in value
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

# New named buffer queries

GetNamedBufferParameterivEXT(buffer, pname, params)
	return		void
	param		buffer		UInt32 in value
	param		pname		VertexBufferObjectParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

GetNamedBufferPointervEXT(buffer, pname, params)
	return		void
	param		buffer		UInt32 in value
	param		pname		VertexBufferObjectParameter in value
	param		params		VoidPointer out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

GetNamedBufferSubDataEXT(buffer, offset, size, data)
	return		void
	param		buffer		UInt32 in value
	param		offset		Intptr in value
	param		size		Sizeiptr in value
	param		data		Void out array [COMPSIZE(size)]
	category	EXT_direct_state_access
	extension	soft WINSOFT
	dlflags		notlistable
	glxflags	ignore
	glfflags	ignore

# New named texture buffer texture object command

TextureBufferEXT(texture, target, internalformat, buffer)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		internalformat	TypeEnum in value
	param		buffer		UInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_texture_buffer_object
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_texture_buffer_object
	dlflags		notlistable

# New named texture buffer multitexture command

MultiTexBufferEXT(texunit, target, internalformat, buffer)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		internalformat	TypeEnum in value
	param		buffer		UInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_texture_buffer_object
	extension	soft WINSOFT NV50
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_texture_buffer_object
	dlflags		notlistable

# New named frame buffer object commands

NamedRenderbufferStorageEXT(renderbuffer, internalformat, width, height)
	return		void
	param		renderbuffer	Renderbuffer in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

GetNamedRenderbufferParameterivEXT(renderbuffer, pname, params)
	return		void
	param		renderbuffer	Renderbuffer in value
	param		pname		RenderbufferParameterName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

CheckNamedFramebufferStatusEXT(framebuffer, target)
	return		FramebufferStatus
	param		framebuffer	Framebuffer in value
	param		target		FramebufferTarget in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

NamedFramebufferTexture1DEXT(framebuffer, attachment, textarget, texture, level)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		textarget	TextureTarget in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

NamedFramebufferTexture2DEXT(framebuffer, attachment, textarget, texture, level)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		textarget	TextureTarget in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

NamedFramebufferTexture3DEXT(framebuffer, attachment, textarget, texture, level, zoffset)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		textarget	TextureTarget in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		zoffset		CheckedInt32 in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

NamedFramebufferRenderbufferEXT(framebuffer, attachment, renderbuffertarget, renderbuffer)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		renderbuffertarget RenderbufferTarget in value
	param		renderbuffer	Renderbuffer in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

GetNamedFramebufferAttachmentParameterivEXT(framebuffer, attachment, pname, params)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		pname		FramebufferAttachmentParameterName in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

GenerateTextureMipmapEXT(texture, target)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

GenerateMultiTexMipmapEXT(texunit, target)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

FramebufferDrawBufferEXT(framebuffer, mode)
	return		void
	param		framebuffer	Framebuffer in value
	param		mode		DrawBufferMode in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

FramebufferDrawBuffersEXT(framebuffer, n, bufs)
	return		void
	param		framebuffer	Framebuffer in value
	param		n		SizeI in value
	param		bufs		DrawBufferMode in array [n]
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

FramebufferReadBufferEXT(framebuffer, mode)
	return		void
	param		framebuffer	Framebuffer in value
	param		mode		ReadBufferMode in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	extension	soft WINSOFT
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_object

GetFramebufferParameterivEXT(framebuffer, pname, params)
	return		void
	param		framebuffer	Framebuffer in value
	param		pname		GetFramebufferParameter in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_object
	dlflags		notlistable
	extension	soft WINSOFT
	glxflags	ignore
	glfflags	capture-execute gl-enum

# New named framebuffer multisample object commands

NamedRenderbufferStorageMultisampleEXT(renderbuffer, samples, internalformat, width, height)
	return		void
	param		renderbuffer	Renderbuffer in value
	param		samples		SizeI in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	subcategory	EXT_framebuffer_multisample
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_EXT_framebuffer_multisample

# New named framebuffer multisample coverage object commands

NamedRenderbufferStorageMultisampleCoverageEXT(renderbuffer, coverageSamples, colorSamples, internalformat, width, height)
	return		void
	param		renderbuffer	Renderbuffer in value
	param		coverageSamples SizeI in value
	param		colorSamples	SizeI in value
	param		internalformat	PixelInternalFormat in value
	param		width		SizeI in value
	param		height		SizeI in value
	category	EXT_direct_state_access
	subcategory	NV_framebuffer_multisample_coverage
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_framebuffer_multisample_coverage

# New named geometry program/shader frame buffer object commands

NamedFramebufferTextureEXT(framebuffer, attachment, texture, level)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedFramebufferTextureLayerEXT(framebuffer, attachment, texture, level, layer)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		layer		CheckedInt32 in value
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

NamedFramebufferTextureFaceEXT(framebuffer, attachment, texture, level, face)
	return		void
	param		framebuffer	Framebuffer in value
	param		attachment	FramebufferAttachment in value
	param		texture		Texture in value
	param		level		CheckedInt32 in value
	param		face		TextureTarget in value
	category	EXT_direct_state_access
	subcategory	NV_gpu_program4
	extension	soft WINSOFT
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_gpu_program4

# New explicit multisample query and commands

TextureRenderbufferEXT(texture, target, renderbuffer)
	return		void
	param		texture		Texture in value
	param		target		TextureTarget in value
	param		renderbuffer	UInt32 in value
	category	EXT_direct_state_access
	subcategory	NV_explicit_multisample
	extension	soft WINSOFT NV50
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_explicit_multisample

MultiTexRenderbufferEXT(texunit, target, renderbuffer)
	return		void
	param		texunit		TextureUnit in value
	param		target		TextureTarget in value
	param		renderbuffer	UInt32 in value
	category	EXT_direct_state_access
	subcategory	NV_explicit_multisample
	extension	soft WINSOFT NV50
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore
	glextmask	GL_MASK_NV_explicit_multisample

# New ARB_gpu_shader_fp64 commands

ProgramUniform1dEXT(program, location, x)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Float64 in value
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2dEXT(program, location, x, y)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3dEXT(program, location, x, y, z)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4dEXT(program, location, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1dvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2dvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count*2]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3dvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count*3]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4dvEXT(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Float64 in array [count*4]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*4]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*9]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*16]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2x3dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*6]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix2x4dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*8]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3x2dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*6]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix3x4dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*12]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4x2dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*8]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformMatrix4x3dvEXT(program, location, count, transpose, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		transpose	Boolean in value
	param		value		Float64 in array [count*12]
	category	EXT_direct_state_access
	subcategory	ARB_gpu_shader_fp64
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #354
# EXT_vertex_array_bgra commands
#
###############################################################################

# (none)
newcategory: EXT_vertex_array_bgra

###############################################################################
#
# Extension #355 - WGL_NV_gpu_affinity
#
###############################################################################

###############################################################################
#
# Extension #356
# EXT_texture_swizzle commands
#
###############################################################################

# (none)
newcategory: EXT_texture_swizzle

###############################################################################
#
# Extension #357
# NV_explicit_multisample commands
#
###############################################################################

# From EXT_draw_buffers2:  GetBooleanIndexedvEXT / GetIntegerIndexedvEXT

GetMultisamplefvNV(pname, index, val)
	return		void
	param		pname		GetMultisamplePNameNV in value
	param		index		UInt32 in value
	param		val		Float32 out array [2]
	category	NV_explicit_multisample
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

SampleMaskIndexedNV(index, mask)
	return		void
	param		index		UInt32 in value
	param		mask		SampleMaskNV in value
	category	NV_explicit_multisample
	glfflags	ignore
	glxflags	ignore

TexRenderbufferNV(target, renderbuffer)
	return		void
	param		target		TextureTarget in value
	param		renderbuffer	UInt32 in value
	category	NV_explicit_multisample
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #358
# NV_transform_feedback2 commands
#
###############################################################################

BindTransformFeedbackNV(target, id)
	return		void
	param		target		BufferTargetARB in value
	param		id		UInt32 in value
	category	NV_transform_feedback2
	glfflags	ignore
	glxflags	ignore

DeleteTransformFeedbacksNV(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 in array [n]
	category	NV_transform_feedback2
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

GenTransformFeedbacksNV(n, ids)
	return		void
	param		n		SizeI in value
	param		ids		UInt32 out array [n]
	category	NV_transform_feedback2
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

IsTransformFeedbackNV(id)
	return		Boolean
	param		id		UInt32 in value
	category	NV_transform_feedback2
	dlflags		notlistable
	glfflags	ignore
	glxflags	ignore

PauseTransformFeedbackNV()
	return		void
	category	NV_transform_feedback2
	glfflags	ignore
	glxflags	ignore

ResumeTransformFeedbackNV()
	return		void
	category	NV_transform_feedback2
	glfflags	ignore
	glxflags	ignore

DrawTransformFeedbackNV(mode, id)
	return		void
	param		mode		GLenum in value
	param		id		UInt32 in value
	category	NV_transform_feedback2
	glfflags	ignore
	glxflags	ignore

###############################################################################
#
# Extension #359
# ATI_meminfo commands
#
###############################################################################

# (none)
newcategory: ATI_meminfo

###############################################################################
#
# Extension #360
# AMD_performance_monitor commands
#
###############################################################################

GetPerfMonitorGroupsAMD(numGroups, groupsSize, groups)
	return		void
	param		numGroups	Int32 out array [1]
	param		groupsSize	SizeI in value
	param		groups		UInt32 out array [groupsSize]
	category	AMD_performance_monitor
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetPerfMonitorCountersAMD(group, numCounters, maxActiveCounters, counterSize, counters)
	return		void
	param		group		UInt32 in value
	param		numCounters	Int32 out array [1]
	param		maxActiveCounters Int32 out array [1]
	param		counterSize	SizeI in value
	param		counters	UInt32 out array [counterSize]
	category	AMD_performance_monitor
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetPerfMonitorGroupStringAMD(group, bufSize, length, groupString)
	return		void
	param		group		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		groupString	Char out array [bufSize]
	category	AMD_performance_monitor
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetPerfMonitorCounterStringAMD(group, counter, bufSize, length, counterString)
	return		void
	param		group		UInt32 in value
	param		counter		UInt32 in value
	param		bufSize		SizeI in value
	param		length		SizeI out array [1]
	param		counterString	Char out array [bufSize]
	category	AMD_performance_monitor
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetPerfMonitorCounterInfoAMD(group, counter, pname, data)
	return		void
	param		group		UInt32 in value
	param		counter		UInt32 in value
	param		pname		GLenum in value
	param		data		Void out array [COMPSIZE(pname)]
	category	AMD_performance_monitor
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GenPerfMonitorsAMD(n, monitors)
	return		void
	param		n		SizeI in value
	param		monitors	UInt32 out array [n]
	category	AMD_performance_monitor
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# 'monitors' is actually in, not out, but extension spec doesn't use const
DeletePerfMonitorsAMD(n, monitors)
	return		void
	param		n		SizeI in value
	param		monitors	UInt32 out array [n]
	category	AMD_performance_monitor
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

# 'counterList' is actually in, not out, but extension spec doesn't use const
SelectPerfMonitorCountersAMD(monitor, enable, group, numCounters, counterList)
	return		void
	param		monitor		UInt32 in value
	param		enable		Boolean in value
	param		group		UInt32 in value
	param		numCounters	Int32 in value
	param		counterList	UInt32 out array [numCounters]
	category	AMD_performance_monitor
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BeginPerfMonitorAMD(monitor)
	return		void
	param		monitor		UInt32 in value
	category	AMD_performance_monitor
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EndPerfMonitorAMD(monitor)
	return		void
	param		monitor		UInt32 in value
	category	AMD_performance_monitor
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetPerfMonitorCounterDataAMD(monitor, pname, dataSize, data, bytesWritten)
	return		void
	param		monitor		UInt32 in value
	param		pname		GLenum in value
	param		dataSize	SizeI in value
	param		data		UInt32 out array [dataSize]
	param		bytesWritten	Int32 out array [1]
	category	AMD_performance_monitor
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #361 - WGL_AMD_gpu_association
#
###############################################################################

###############################################################################
#
# Extension #362
# AMD_texture_texture4 commands
#
###############################################################################

# (none)
newcategory: AMD_texture_texture4

###############################################################################
#
# Extension #363
# AMD_vertex_shader_tessellator commands
#
###############################################################################

TessellationFactorAMD(factor)
	return		void
	param		factor		Float32 in value
	category	AMD_vertex_shader_tessellator
	version		2.0
	glxsingle	?
	glxflags	ignore
	offset		?

TessellationModeAMD(mode)
	return		void
	param		mode		GLenum in value
	category	AMD_vertex_shader_tessellator
	version		2.0
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #364
# EXT_provoking_vertex commands
#
###############################################################################

ProvokingVertexEXT(mode)
	return		void
	param		mode		GLenum in value
	category	EXT_provoking_vertex
	version		2.1
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #365
# EXT_texture_snorm commands
#
###############################################################################

# (none)
newcategory: EXT_texture_snorm

###############################################################################
#
# Extension #366
# AMD_draw_buffers_blend commands
#
###############################################################################

BlendFuncIndexedAMD(buf, src, dst)
	return		void
	param		buf		UInt32 in value
	param		src		GLenum in value
	param		dst		GLenum in value
	category	AMD_draw_buffers_blend
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendFuncSeparateIndexedAMD(buf, srcRGB, dstRGB, srcAlpha, dstAlpha)
	return		void
	param		buf		UInt32 in value
	param		srcRGB		GLenum in value
	param		dstRGB		GLenum in value
	param		srcAlpha	GLenum in value
	param		dstAlpha	GLenum in value
	category	AMD_draw_buffers_blend
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendEquationIndexedAMD(buf, mode)
	return		void
	param		buf		UInt32 in value
	param		mode		GLenum in value
	category	AMD_draw_buffers_blend
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BlendEquationSeparateIndexedAMD(buf, modeRGB, modeAlpha)
	return		void
	param		buf		UInt32 in value
	param		modeRGB		GLenum in value
	param		modeAlpha	GLenum in value
	category	AMD_draw_buffers_blend
	version		2.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #367
# APPLE_texture_range commands
#
###############################################################################

TextureRangeAPPLE(target, length, pointer)
	return		void
	param		target		GLenum in value
	param		length		SizeI in value
	param		pointer		Void in array [length]
	category	APPLE_texture_range
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetTexParameterPointervAPPLE(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		VoidPointer out array [1]
	category	APPLE_texture_range
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #368
# APPLE_float_pixels commands
#
###############################################################################

# (none)
newcategory: APPLE_float_pixels

###############################################################################
#
# Extension #369
# APPLE_vertex_program_evaluators commands
#
###############################################################################

EnableVertexAttribAPPLE(index, pname)
	return		void
	param		index		UInt32 in value
	param		pname		GLenum in value
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DisableVertexAttribAPPLE(index, pname)
	return		void
	param		index		UInt32 in value
	param		pname		GLenum in value
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsVertexAttribEnabledAPPLE(index, pname)
	return		Boolean
	param		index		UInt32 in value
	param		pname		GLenum in value
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapVertexAttrib1dAPPLE(index, size, u1, u2, stride, order, points)
	return		void
	param		index		UInt32 in value
	param		size		UInt32 in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	param		stride		Int32 in value
	param		order		CheckedInt32 in value
	param		points		CoordD in array [COMPSIZE(size/stride/order)]
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapVertexAttrib1fAPPLE(index, size, u1, u2, stride, order, points)
	return		void
	param		index		UInt32 in value
	param		size		UInt32 in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	param		stride		Int32 in value
	param		order		CheckedInt32 in value
	param		points		CoordF in array [COMPSIZE(size/stride/order)]
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapVertexAttrib2dAPPLE(index, size, u1, u2, ustride, uorder, v1, v2, vstride, vorder, points)
	return		void
	param		index		UInt32 in value
	param		size		UInt32 in value
	param		u1		CoordD in value
	param		u2		CoordD in value
	param		ustride		Int32 in value
	param		uorder		CheckedInt32 in value
	param		v1		CoordD in value
	param		v2		CoordD in value
	param		vstride		Int32 in value
	param		vorder		CheckedInt32 in value
	param		points		CoordD in array [COMPSIZE(size/ustride/uorder/vstride/vorder)]
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapVertexAttrib2fAPPLE(index, size, u1, u2, ustride, uorder, v1, v2, vstride, vorder, points)
	return		void
	param		index		UInt32 in value
	param		size		UInt32 in value
	param		u1		CoordF in value
	param		u2		CoordF in value
	param		ustride		Int32 in value
	param		uorder		CheckedInt32 in value
	param		v1		CoordF in value
	param		v2		CoordF in value
	param		vstride		Int32 in value
	param		vorder		CheckedInt32 in value
	param		points		CoordF in array [COMPSIZE(size/ustride/uorder/vstride/vorder)]
	category	APPLE_vertex_program_evaluators
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #370
# APPLE_aux_depth_stencil commands
#
###############################################################################

# (none)
newcategory: APPLE_aux_depth_stencil

###############################################################################
#
# Extension #371
# APPLE_object_purgeable commands
#
###############################################################################

ObjectPurgeableAPPLE(objectType, name, option)
	return		GLenum
	param		objectType	GLenum in value
	param		name		UInt32 in value
	param		option		GLenum in value
	category	APPLE_object_purgeable
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ObjectUnpurgeableAPPLE(objectType, name, option)
	return		GLenum
	param		objectType	GLenum in value
	param		name		UInt32 in value
	param		option		GLenum in value
	category	APPLE_object_purgeable
	version		1.5
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetObjectParameterivAPPLE(objectType, name, pname, params)
	return		void
	param		objectType	GLenum in value
	param		name		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	APPLE_object_purgeable
	dlflags		notlistable
	version		1.5
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #372
# APPLE_row_bytes commands
#
###############################################################################

# (none)
newcategory: APPLE_row_bytes

###############################################################################
#
# Extension #373
# APPLE_rgb_422 commands
#
###############################################################################

# (none)
newcategory: APPLE_rgb_422

###############################################################################
#
# Extension #374
# NV_video_capture commands
#
###############################################################################

BeginVideoCaptureNV(video_capture_slot)
	return		void
	param		video_capture_slot	UInt32 in value
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindVideoCaptureStreamBufferNV(video_capture_slot, stream, frame_region, offset)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		frame_region	GLenum in value
	param		offset		BufferOffsetARB in value
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

BindVideoCaptureStreamTextureNV(video_capture_slot, stream, frame_region, target, texture)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		frame_region	GLenum in value
	param		target		GLenum in value
	param		texture		UInt32 in value
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EndVideoCaptureNV(video_capture_slot)
	return		void
	param		video_capture_slot	UInt32 in value
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVideoCaptureivNV(video_capture_slot, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	NV_video_capture
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVideoCaptureStreamivNV(video_capture_slot, stream, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 out array [COMPSIZE(pname)]
	category	NV_video_capture
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVideoCaptureStreamfvNV(video_capture_slot, stream, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		pname		GLenum in value
	param		params		Float32 out array [COMPSIZE(pname)]
	category	NV_video_capture
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVideoCaptureStreamdvNV(video_capture_slot, stream, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		pname		GLenum in value
	param		params		Float64 out array [COMPSIZE(pname)]
	category	NV_video_capture
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

VideoCaptureNV(video_capture_slot, sequence_num, capture_time)
	return		GLenum
	param		video_capture_slot	UInt32 in value
	param		sequence_num	UInt32 out reference
	param		capture_time	UInt64EXT out reference
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VideoCaptureStreamParameterivNV(video_capture_slot, stream, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		pname		GLenum in value
	param		params		Int32 in array [COMPSIZE(pname)]
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VideoCaptureStreamParameterfvNV(video_capture_slot, stream, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		pname		GLenum in value
	param		params		Float32 in array [COMPSIZE(pname)]
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VideoCaptureStreamParameterdvNV(video_capture_slot, stream, pname, params)
	return		void
	param		video_capture_slot	UInt32 in value
	param		stream		UInt32 in value
	param		pname		GLenum in value
	param		params		Float64 in array [COMPSIZE(pname)]
	category	NV_video_capture
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #375 - GLX_EXT_swap_control
#
###############################################################################

###############################################################################
#
# Extension #376 - also GLX_NV_copy_image, WGL_NV_copy_image
# NV_copy_image commands
#
###############################################################################

CopyImageSubDataNV(srcName, srcTarget, srcLevel, srcX, srcY, srcZ, dstName, dstTarget, dstLevel, dstX, dstY, dstZ, width, height, depth)
	return		void
	param		srcName		UInt32 in value
	param		srcTarget	GLenum in value
	param		srcLevel	Int32 in value
	param		srcX		Int32 in value
	param		srcY		Int32 in value
	param		srcZ		Int32 in value
	param		dstName		UInt32 in value
	param		dstTarget	GLenum in value
	param		dstLevel	Int32 in value
	param		dstX		Int32 in value
	param		dstY		Int32 in value
	param		dstZ		Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	category	NV_copy_image
	version		1.2
	extension
	glxropcode	4291
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #377
# EXT_separate_shader_objects commands
#
###############################################################################

UseShaderProgramEXT(type, program)
	return		void
	param		type		GLenum in value
	param		program		UInt32 in value
	category	EXT_separate_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ActiveProgramEXT(program)
	return		void
	param		program		UInt32 in value
	category	EXT_separate_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

CreateShaderProgramEXT(type, string)
	return		UInt32
	param		type		GLenum in value
	param		string		Char in array []
	category	EXT_separate_shader_objects
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #378
# NV_parameter_buffer_object2 commands
#
###############################################################################

# (none)
newcategory: NV_parameter_buffer_object2

###############################################################################
#
# Extension #379
# NV_shader_buffer_load commands
#
###############################################################################

MakeBufferResidentNV(target, access)
	return		void
	param		target		GLenum in value
	param		access		GLenum in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MakeBufferNonResidentNV(target)
	return		void
	param		target		GLenum in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsBufferResidentNV(target)
	return		Boolean
	param		target		GLenum in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MakeNamedBufferResidentNV(buffer, access)
	return		void
	param		buffer		UInt32 in value
	param		access		GLenum in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MakeNamedBufferNonResidentNV(buffer)
	return		void
	param		buffer		UInt32 in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsNamedBufferResidentNV(buffer)
	return		Boolean
	param		buffer		UInt32 in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetBufferParameterui64vNV(target, pname, params)
	return		void
	param		target		GLenum in value
	param		pname		GLenum in value
	param		params		UInt64EXT out array [COMPSIZE(pname)]
	category	NV_shader_buffer_load
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetNamedBufferParameterui64vNV(buffer, pname, params)
	return		void
	param		buffer		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt64EXT out array [COMPSIZE(pname)]
	category	NV_shader_buffer_load
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetIntegerui64vNV(value, result)
	return		void
	param		value		GLenum in value
	param		result		UInt64EXT out array [COMPSIZE(value)]
	category	NV_shader_buffer_load
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

Uniformui64NV(location, value)
	return		void
	param		location	Int32 in value
	param		value		UInt64EXT in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniformui64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [count]
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetUniformui64vNV(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		UInt64EXT out array [COMPSIZE(program/location)]
	category	NV_shader_buffer_load
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

ProgramUniformui64NV(program, location, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		value		UInt64EXT in value
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformui64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [count]
	category	NV_shader_buffer_load
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #380
# NV_vertex_buffer_unified_memory commands
#
###############################################################################

BufferAddressRangeNV(pname, index, address, length)
	return		void
	param		pname		GLenum in value
	param		index		UInt32 in value
	param		address		UInt64EXT in value
	param		length		BufferSize in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexFormatNV(size, type, stride)
	return		void
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

NormalFormatNV(type, stride)
	return		void
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ColorFormatNV(size, type, stride)
	return		void
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IndexFormatNV(type, stride)
	return		void
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexCoordFormatNV(size, type, stride)
	return		void
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EdgeFlagFormatNV(stride)
	return		void
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

SecondaryColorFormatNV(size, type, stride)
	return		void
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

FogCoordFormatNV(type, stride)
	return		void
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribFormatNV(index, size, type, normalized, stride)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		normalized	Boolean in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribIFormatNV(index, size, type, stride)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_buffer_unified_memory
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetIntegerui64i_vNV(value, index, result)
	return		void
	param		value		GLenum in value
	param		index		UInt32 in value
	param		result		UInt64EXT out array [COMPSIZE(value)]
	category	NV_vertex_buffer_unified_memory
	dlflags		notlistable
	version		1.2
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #381
# NV_texture_barrier commands
#
###############################################################################

TextureBarrierNV()
	return		void
	category	NV_texture_barrier
	version		1.2
	extension
	glxropcode	4348
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #382
# AMD_shader_stencil_export commands
#
###############################################################################

# (none)
newcategory: AMD_shader_stencil_export

###############################################################################
#
# Extension #383
# AMD_seamless_cubemap_per_texture commands
#
###############################################################################

# (none)
newcategory: AMD_seamless_cubemap_per_texture

###############################################################################
#
# Extension #384 - GLX_INTEL_swap_event
#
###############################################################################

###############################################################################
#
# Extension #385
# AMD_conservative_depth commands
#
###############################################################################

# (none)
newcategory: AMD_conservative_depth

###############################################################################
#
# Extension #386
# EXT_shader_image_load_store commands
#
###############################################################################

BindImageTextureEXT(index, texture, level, layered, layer, access, format)
	return		void
	param		index		UInt32 in value
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		layered		Boolean in value
	param		layer		Int32 in value
	param		access		GLenum in value
	param		format		Int32 in value
	category	EXT_shader_image_load_store
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MemoryBarrierEXT(barriers)
	return		void
	param		barriers	GLbitfield in value
	category	EXT_shader_image_load_store
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #387
# EXT_vertex_attrib_64bit commands
#
###############################################################################

VertexAttribL1dEXT(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2dEXT(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3dEXT(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4dEXT(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Float64 in value
	param		y		Float64 in value
	param		z		Float64 in value
	param		w		Float64 in value
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL1dvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [1]
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2dvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [2]
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3dvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [3]
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4dvEXT(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Float64 in array [4]
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribLPointerEXT(index, size, type, stride, pointer)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	param		pointer		Void in array [size]
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVertexAttribLdvEXT(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		GLenum in value
	param		params		Float64 out array [COMPSIZE(pname)]
	category	EXT_vertex_attrib_64bit
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

# Also in ARB_vertex_array_64bit. Supposedly dependent on another
# unregistered extension, EXT_direct_state_access_memory

VertexArrayVertexAttribLOffsetEXT(vaobj, buffer, index, size, type, stride, offset)
	return		void
	param		vaobj		UInt32 in value
	param		buffer		UInt32 in value
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	param		offset		BufferOffset in value
	category	EXT_vertex_attrib_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #388
# NV_gpu_program5 commands
#
###############################################################################

# These commands require ARB_shader_subroutine

ProgramSubroutineParametersuivNV(target, count, params)
	return		void
	param		target		GLenum in value
	param		count		SizeI in value
	param		params		UInt32 in array [count]
	category	NV_gpu_program5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetProgramSubroutineParameteruivNV(target, index, param)
	return		void
	param		target		GLenum in value
	param		index		UInt32 in value
	param		param		UInt32 out array [COMPSIZE(target)]
	category	NV_gpu_program5
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #389
# NV_gpu_shader5 commands
#
###############################################################################

Uniform1i64NV(location, x)
	return		void
	param		location	Int32 in value
	param		x		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2i64NV(location, x, y)
	return		void
	param		location	Int32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3i64NV(location, x, y, z)
	return		void
	param		location	Int32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	param		z		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4i64NV(location, x, y, z, w)
	return		void
	param		location	Int32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	param		z		Int64EXT in value
	param		w		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1i64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [count]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2i64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [COMPSIZE(count*2)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3i64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [COMPSIZE(count*3)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4i64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [COMPSIZE(count*4)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1ui64NV(location, x)
	return		void
	param		location	Int32 in value
	param		x		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2ui64NV(location, x, y)
	return		void
	param		location	Int32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3ui64NV(location, x, y, z)
	return		void
	param		location	Int32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	param		z		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4ui64NV(location, x, y, z, w)
	return		void
	param		location	Int32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	param		z		UInt64EXT in value
	param		w		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform1ui64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [count]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform2ui64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [COMPSIZE(count*2)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform3ui64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [COMPSIZE(count*3)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

Uniform4ui64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [COMPSIZE(count*4)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetUniformi64vNV(program, location, params)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		params		Int64EXT out array [COMPSIZE(location)]
	category	NV_gpu_shader5
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

ProgramUniform1i64NV(program, location, x)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2i64NV(program, location, x, y)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3i64NV(program, location, x, y, z)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	param		z		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4i64NV(program, location, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	param		z		Int64EXT in value
	param		w		Int64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1i64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [count]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2i64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [COMPSIZE(count*2)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3i64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [COMPSIZE(count*3)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4i64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		Int64EXT in array [COMPSIZE(count*4)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1ui64NV(program, location, x)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2ui64NV(program, location, x, y)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3ui64NV(program, location, x, y, z)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	param		z		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4ui64NV(program, location, x, y, z, w)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	param		z		UInt64EXT in value
	param		w		UInt64EXT in value
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform1ui64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [count]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform2ui64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [COMPSIZE(count*2)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform3ui64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [COMPSIZE(count*3)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniform4ui64vNV(program, location, count, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64EXT in array [COMPSIZE(count*4)]
	category	NV_gpu_shader5
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

#@ GetUniformui64vNV also in NV_shader_buffer_load

###############################################################################
#
# Extension #390
# NV_shader_buffer_store commands
#
###############################################################################

# (none)
newcategory: NV_shader_buffer_store

###############################################################################
#
# Extension #391
# NV_tessellation_program5 commands
#
###############################################################################

# (none)
newcategory: NV_tessellation_program5

###############################################################################
#
# Extension #392
# NV_vertex_attrib_integer_64bit commands
#
###############################################################################

VertexAttribL1i64NV(index, x)
	return		void
	param		index		UInt32 in value
	param		x		Int64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2i64NV(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3i64NV(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	param		z		Int64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4i64NV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		Int64EXT in value
	param		y		Int64EXT in value
	param		z		Int64EXT in value
	param		w		Int64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL1i64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int64EXT in array [1]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2i64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int64EXT in array [2]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3i64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int64EXT in array [3]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4i64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		Int64EXT in array [4]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL1ui64NV(index, x)
	return		void
	param		index		UInt32 in value
	param		x		UInt64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2ui64NV(index, x, y)
	return		void
	param		index		UInt32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3ui64NV(index, x, y, z)
	return		void
	param		index		UInt32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	param		z		UInt64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4ui64NV(index, x, y, z, w)
	return		void
	param		index		UInt32 in value
	param		x		UInt64EXT in value
	param		y		UInt64EXT in value
	param		z		UInt64EXT in value
	param		w		UInt64EXT in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL1ui64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt64EXT in array [1]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL2ui64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt64EXT in array [2]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL3ui64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt64EXT in array [3]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VertexAttribL4ui64vNV(index, v)
	return		void
	param		index		UInt32 in value
	param		v		UInt64EXT in array [4]
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetVertexAttribLi64vNV(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		GLenum in value
	param		params		Int64EXT out array [COMPSIZE(pname)]
	category	NV_vertex_attrib_integer_64bit
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetVertexAttribLui64vNV(index, pname, params)
	return		void
	param		index		UInt32 in value
	param		pname		GLenum in value
	param		params		UInt64EXT out array [COMPSIZE(pname)]
	category	NV_vertex_attrib_integer_64bit
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

#@ VertexAttribLFormatNV also requires NV_vertex_buffer_unified_memory

VertexAttribLFormatNV(index, size, type, stride)
	return		void
	param		index		UInt32 in value
	param		size		Int32 in value
	param		type		GLenum in value
	param		stride		SizeI in value
	category	NV_vertex_attrib_integer_64bit
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #393
# NV_multisample_coverage commands
#
###############################################################################

# (none)
newcategory: NV_multisample_coverage

###############################################################################
#
# Extension #394
# AMD_name_gen_delete commands
#
###############################################################################

GenNamesAMD(identifier, num, names)
	return		void
	param		identifier	GLenum in value
	param		num		UInt32 in value
	param		names		UInt32 out array [num]
	category	AMD_name_gen_delete
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DeleteNamesAMD(identifier, num, names)
	return		void
	param		identifier	GLenum in value
	param		num		UInt32 in value
	param		names		UInt32 in array [num]
	category	AMD_name_gen_delete
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsNameAMD(identifier, name)
	return		Boolean
	param		identifier	GLenum in value
	param		name		UInt32 in value
	category	AMD_name_gen_delete
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #395
# AMD_debug_output commands
#
###############################################################################

DebugMessageEnableAMD(category, severity, count, ids, enabled)
	return		void
	param		category	GLenum in value
	param		severity	GLenum in value
	param		count		SizeI in value
	param		ids		UInt32 in array [count]
	param		enabled		Boolean in value
	category	AMD_debug_output
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DebugMessageInsertAMD(category, severity, id, length, buf)
	return		void
	param		category	GLenum in value
	param		severity	GLenum in value
	param		id		UInt32 in value
	param		length		SizeI in value
	param		buf		Char in array [length]
	category	AMD_debug_output
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

DebugMessageCallbackAMD(callback, userParam)
	return		void
	param		callback	GLDEBUGPROCAMD in value
	param		userParam	Void out reference
	category	AMD_debug_output
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetDebugMessageLogAMD(count, bufsize, categories, severities, ids, lengths, message)
	return		UInt32
	param		count		UInt32 in value
	param		bufsize		SizeI in value
	param		categories	GLenum out array [count]
	param		severities	UInt32 out array [count]
	param		ids		UInt32 out array [count]
	param		lengths		SizeI out array [count]
	param		message		Char out array [bufsize]
	category	AMD_debug_output
	dlflags		notlistable
	version		4.1
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #396
# NV_vdpau_interop commands
#
###############################################################################

VDPAUInitNV(vdpDevice, getProcAddress)
	return		void
	param		vdpDevice	Void in reference
	param		getProcAddress	Void in reference
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUFiniNV()
	return		void
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAURegisterVideoSurfaceNV(vdpSurface, target, numTextureNames, textureNames)
	return		vdpauSurfaceNV
	param		vdpSurface	Void in reference
	param		target		GLenum in value
	param		numTextureNames SizeI in value
	param		textureNames	UInt32 in array [numTextureNames]
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAURegisterOutputSurfaceNV(vdpSurface, target, numTextureNames, textureNames)
	return		vdpauSurfaceNV
	param		vdpSurface	Void out reference
	param		target		GLenum in value
	param		numTextureNames SizeI in value
	param		textureNames	UInt32 in array [numTextureNames]
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUIsSurfaceNV(surface)
	return		void
	param		surface		vdpauSurfaceNV in value
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUUnregisterSurfaceNV(surface)
	return		void
	param		surface		vdpauSurfaceNV in value
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUGetSurfaceivNV(surface, pname, bufSize, length, values)
	return		void
	param		surface		vdpauSurfaceNV in value
	param		pname		GLenum in value
	param		bufSize		SizeI in value
	param		length		SizeI out reference
	param		values		Int32 out array [length]
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUSurfaceAccessNV(surface, access)
	return		void
	param		surface		vdpauSurfaceNV in value
	param		access		GLenum in value
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUMapSurfacesNV(numSurfaces, surfaces)
	return		void
	param		numSurfaces	SizeI in value
	param		surfaces	vdpauSurfaceNV in array [numSurfaces]
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

VDPAUUnmapSurfacesNV(numSurface, surfaces)
	return		void
	param		numSurface	SizeI in value
	param		surfaces	vdpauSurfaceNV in array [numSurface]
	category	NV_vdpau_interop
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?


###############################################################################
#
# Extension #397
# AMD_transform_feedback3_lines_triangles commands
#
###############################################################################

# (none)
newcategory: AMD_transform_feedback3_lines_triangles

###############################################################################
#
# Extension #398 - GLX_AMD_gpu_association
# Extension #399 - GLX_EXT_create_context_es2_profile
# Extension #400 - WGL_EXT_create_context_es2_profile
#
###############################################################################

###############################################################################
#
# Extension #401
# AMD_depth_clamp_separate commands
#
###############################################################################

# (none)
newcategory: AMD_depth_clamp_separate

###############################################################################
#
# Extension #402
# EXT_texture_sRGB_decode commands
#
###############################################################################

# (none)
newcategory: EXT_texture_sRGB_decode

###############################################################################
#
# Extension #403
# NV_texture_multisample commands
#
###############################################################################

TexImage2DMultisampleCoverageNV(target, coverageSamples, colorSamples, internalFormat, width, height, fixedSampleLocations)
	return		void
	param		target		GLenum in value
	param		coverageSamples SizeI in value
	param		colorSamples	SizeI in value
	param		internalFormat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		fixedSampleLocations	Boolean in value
	category	NV_texture_multisample
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TexImage3DMultisampleCoverageNV(target, coverageSamples, colorSamples, internalFormat, width, height, depth, fixedSampleLocations)
	return		void
	param		target		GLenum in value
	param		coverageSamples SizeI in value
	param		colorSamples	SizeI in value
	param		internalFormat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		fixedSampleLocations	Boolean in value
	category	NV_texture_multisample
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureImage2DMultisampleNV(texture, target, samples, internalFormat, width, height, fixedSampleLocations)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalFormat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		fixedSampleLocations	Boolean in value
	category	NV_texture_multisample
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureImage3DMultisampleNV(texture, target, samples, internalFormat, width, height, depth, fixedSampleLocations)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		samples		SizeI in value
	param		internalFormat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		fixedSampleLocations	Boolean in value
	category	NV_texture_multisample
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureImage2DMultisampleCoverageNV(texture, target, coverageSamples, colorSamples, internalFormat, width, height, fixedSampleLocations)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		coverageSamples SizeI in value
	param		colorSamples	SizeI in value
	param		internalFormat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		fixedSampleLocations	Boolean in value
	category	NV_texture_multisample
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureImage3DMultisampleCoverageNV(texture, target, coverageSamples, colorSamples, internalFormat, width, height, depth, fixedSampleLocations)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		coverageSamples SizeI in value
	param		colorSamples	SizeI in value
	param		internalFormat	Int32 in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		fixedSampleLocations	Boolean in value
	category	NV_texture_multisample
	version		4.1
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #404
# AMD_blend_minmax_factor commands
#
###############################################################################

# (none)
newcategory: AMD_blend_minmax_factor

###############################################################################
#
# Extension #405
# AMD_sample_positions commands
#
###############################################################################

SetMultisamplefvAMD(pname, index, val)
	return		void
	param		pname		GLenum in value
	param		index		UInt32 in value
	param		val		Float32 in array [2]
	category	AMD_sample_positions
	glxflags	ignore
	version		3.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #406
# EXT_x11_sync_object commands
#
###############################################################################

ImportSyncEXT(external_sync_type, external_sync, flags)
	return		sync
	param		external_sync_type  GLenum in value
	param		external_sync	Intptr in value
	param		flags		GLbitfield in value
	category	EXT_x11_sync_object
	glxflags	ignore
	version		3.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #407 - WGL_NV_DX_interop
#
###############################################################################

###############################################################################
#
# Extension #408
# AMD_multi_draw_indirect commands
#
###############################################################################

MultiDrawArraysIndirectAMD(mode, indirect, primcount, stride)
	return		void
	param		mode		GLenum in value
	param		indirect	Void in array []
	param		primcount	SizeI in value
	param		stride		SizeI in value
	category	AMD_multi_draw_indirect
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MultiDrawElementsIndirectAMD(mode, type, indirect, primcount, stride)
	return		void
	param		mode		GLenum in value
	param		type		GLenum in value
	param		indirect	Void in array []
	param		primcount	SizeI in value
	param		stride		SizeI in value
	category	AMD_multi_draw_indirect
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #409
# EXT_framebuffer_multisample_blit_scaled commands
#
###############################################################################

# (none)
newcategory: EXT_framebuffer_multisample_blit_scaled

###############################################################################
#
# Extension #410
# NV_path_rendering commands
#
###############################################################################

# PATH NAME MANAGMENT

GenPathsNV(range)
	return		Path
	param		range		    SizeI in value
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

DeletePathsNV(path, range)
	return		void
	param		path		Path in value
	param		range		SizeI in value
	dlflags		notlistable
	category	NV_path_rendering
	version		1.1
	extension

IsPathNV(path)
	return		Boolean
	param		path	     Path in value
	dlflags		notlistable
	category	NV_path_rendering
	version		1.1
	extension

# PATH SPECIFICATION COMMANDS

PathCommandsNV(path, numCommands, commands, numCoords, coordType, coords)
	return		void
	param		path		Path in value
	param		numCommands	SizeI in value
	param		commands	PathCommand in array [numCommands]
	param		numCoords	SizeI in value
	param		coordType	PathCoordType in value
	param		coords		Void in array [COMPSIZE(numCoords,coordType)]
	category	NV_path_rendering
	version		1.1
	extension

PathCoordsNV(path, numCoords, coordType, coords)
	return		void
	param		path		Path in value
	param		numCoords	SizeI in value
	param		coordType	PathCoordType in value
	param		coords		Void in array [COMPSIZE(numCoords,coordType)]
	category	NV_path_rendering
	version		1.1
	extension

PathSubCommandsNV(path, commandStart, commandsToDelete, numCommands, commands, numCoords, coordType, coords)
	return		void
	param		path		Path in value
	param		commandStart	SizeI in value
	param		commandsToDelete SizeI in value
	param		numCommands	SizeI in value
	param		commands	PathCommand in array [numCommands]
	param		numCoords	SizeI in value
	param		coordType	PathCoordType in value
	param		coords		Void in array [COMPSIZE(numCoords,coordType)]
	category	NV_path_rendering
	version		1.1
	extension

PathSubCoordsNV(path, coordStart, numCoords, coordType, coords)
	return		void
	param		path		Path in value
	param		coordStart	SizeI in value
	param		numCoords	SizeI in value
	param		coordType	PathCoordType in value
	param		coords		Void in array [COMPSIZE(numCoords,coordType)]
	category	NV_path_rendering
	version		1.1
	extension

PathStringNV(path, format, length, pathString)
	return		void
	param		path		Path in value
	param		format		PathStringFormat in value
	param		length		SizeI in value
	param		pathString	Void in array [length]
	category	NV_path_rendering
	version		1.1
	extension

PathGlyphsNV(firstPathName, fontTarget, fontName, fontStyle, numGlyphs, type, charcodes, handleMissingGlyphs, pathParameterTemplate, emScale)
	return		void
	param		firstPathName	Path in value
	param		fontTarget	PathFontTarget in value
	param		fontName	Void in array [COMPSIZE(fontTarget,fontName)]
	param		fontStyle	PathFontStyle in value
	param		numGlyphs	SizeI in value
	param		type		PathElementType in value
	param		charcodes	Void in array [COMPSIZE(numGlyphs,type,charcodes)]
	param		handleMissingGlyphs PathHandleMissingGlyphs in value
	param		pathParameterTemplate Path in value
	param		emScale		Float32 in value
	category	NV_path_rendering
	version		1.1
	extension

PathGlyphRangeNV(firstPathName, fontTarget, fontName, fontStyle, firstGlyph, numGlyphs, handleMissingGlyphs, pathParameterTemplate, emScale)
	return		void
	param		firstPathName	Path in value
	param		fontTarget	PathFontTarget in value
	param		fontName	Void in array [COMPSIZE(fontTarget,fontName)]
	param		fontStyle	PathFontStyle in value
	param		firstGlyph	UInt32 in value
	param		numGlyphs	SizeI in value
	param		handleMissingGlyphs PathHandleMissingGlyphs in value
	param		pathParameterTemplate Path in value
	param		emScale		Float32 in value
	category	NV_path_rendering
	version		1.1
	extension
	dlflags		prepad

WeightPathsNV(resultPath, numPaths, paths, weights)
	return		void
	param		resultPath	Path in value
	param		numPaths	SizeI in value
	param		paths		Path in array [numPaths]
	param		weights		Float32 in array [numPaths]
	category	NV_path_rendering
	version		1.1
	extension

CopyPathNV(resultPath, srcPath)
	return		void
	param		resultPath	Path in value
	param		srcPath		Path in value
	category	NV_path_rendering
	version		1.1
	extension

InterpolatePathsNV(resultPath, pathA, pathB, weight)
	return		void
	param		resultPath	Path in value
	param		pathA		Path in value
	param		pathB		Path in value
	param		weight		Float32 in value
	category	NV_path_rendering
	version		1.1
	extension

TransformPathNV(resultPath, srcPath, transformType, transformValues)
	return		void
	param		resultPath	Path in value
	param		srcPath		Path in value
	param		transformType	PathTransformType in value
	param		transformValues Float32 in array [COMPSIZE(transformType)]
	category	NV_path_rendering
	version		1.1
	extension

PathParameterivNV(path, pname, value)
	return		void
	param		path		Path in value
	param		pname		PathParameter in value
	param		value		Int32 in array [COMPSIZE(pname)]
	category	NV_path_rendering
	version		1.1
	extension

PathParameteriNV(path, pname, value)
	return		void
	param		path		Path in value
	param		pname		PathParameter in value
	param		value		Int32 in value
	category	NV_path_rendering
	version		1.1
	extension

PathParameterfvNV(path, pname, value)
	return		void
	param		path		Path in value
	param		pname		PathParameter in value
	param		value		Float32 in array [COMPSIZE(pname)]
	category	NV_path_rendering
	version		1.1
	extension

PathParameterfNV(path, pname, value)
	return		void
	param		path		Path in value
	param		pname		PathParameter in value
	param		value		Float32 in value
	category	NV_path_rendering
	version		1.1
	extension

PathDashArrayNV(path, dashCount, dashArray)
	return		void
	param		path		Path in value
	param		dashCount	SizeI in value
	param		dashArray	Float32 in array [dashCount]
	category	NV_path_rendering
	version		1.1
	extension

# PATH STENCILING

PathStencilFuncNV(func, ref, mask)
	return		void
	param		func		StencilFunction in value
	param		ref		ClampedStencilValue in value
	param		mask		MaskedStencilValue in value
	category	NV_path_rendering
	version		1.1
	extension

PathStencilDepthOffsetNV(factor, units)
	return		void
	param		factor		Float32 in value
	param		units		Float32 in value
	category	NV_path_rendering
	version		1.1
	extension

StencilFillPathNV(path, fillMode, mask)
	return		void
	param		path		Path in value
	param		fillMode	PathFillMode in value
	param		mask		MaskedStencilValue in value
	category	NV_path_rendering
	version		1.1
	extension

StencilStrokePathNV(path, reference, mask)
	return		void
	param		path		Path in value
	param		reference	StencilValue in value
	param		mask		MaskedStencilValue in value
	category	NV_path_rendering
	version		1.1
	extension

StencilFillPathInstancedNV(numPaths, pathNameType, paths, pathBase, fillMode, mask, transformType, transformValues)
	return		void
	param		numPaths	SizeI in value
	param		pathNameType	PathElementType in value
	param		paths		PathElement in array [COMPSIZE(numPaths,pathNameType,paths)]
	param		pathBase	Path in value
	param		fillMode	PathFillMode in value
	param		mask		MaskedStencilValue in value
	param		transformType	PathTransformType in value
	param		transformValues Float32 in array [COMPSIZE(numPaths,transformType)]
	category	NV_path_rendering
	version		1.1
	extension

StencilStrokePathInstancedNV(numPaths, pathNameType, paths, pathBase, reference, mask, transformType, transformValues)
	return		void
	param		numPaths	SizeI in value
	param		pathNameType	PathElementType in value
	param		paths		PathElement in array [COMPSIZE(numPaths,pathNameType,paths)]
	param		pathBase	Path in value
	param		reference	StencilValue in value
	param		mask		MaskedStencilValue in value
	param		transformType	PathTransformType in value
	param		transformValues Float32 in array [COMPSIZE(numPaths,transformType)]
	category	NV_path_rendering
	version		1.1
	extension

# PATH COVERING

PathCoverDepthFuncNV(func)
	return		void
	param		func		DepthFunction in value
	category	NV_path_rendering
	version		1.1
	extension

PathColorGenNV(color, genMode, colorFormat, coeffs)
	return		void
	param		color		PathColor in value
	param		genMode		PathGenMode in value
	param		colorFormat	PathColorFormat in value
	param		coeffs		Float32 in array [COMPSIZE(genMode,colorFormat)]
	category	NV_path_rendering
	version		1.1
	extension

PathTexGenNV(texCoordSet, genMode, components, coeffs)
	return		void
	param		texCoordSet	PathColor in value
	param		genMode		PathGenMode in value
	param		components	Int32 in value
	param		coeffs		Float32 in array [COMPSIZE(genMode,components)]
	category	NV_path_rendering
	version		1.1
	extension

PathFogGenNV(genMode)
	return		void
	param		genMode		PathGenMode in value
	category	NV_path_rendering
	version		1.1
	extension

CoverFillPathNV(path, coverMode)
	return		void
	param		path		Path in value
	param		coverMode	PathCoverMode in value
	category	NV_path_rendering
	version		1.1
	extension

CoverStrokePathNV(path, coverMode)
	return		void
	param		path		Path in value
	param		coverMode	PathCoverMode in value
	category	NV_path_rendering
	version		1.1
	extension

CoverFillPathInstancedNV(numPaths, pathNameType, paths, pathBase, coverMode, transformType, transformValues)
	return		void
	param		numPaths	SizeI in value
	param		pathNameType	PathElementType in value
	param		paths		PathElement in array [COMPSIZE(numPaths,pathNameType,paths)]
	param		pathBase	Path in value
	param		coverMode	PathCoverMode in value
	param		transformType	PathTransformType in value
	param		transformValues Float32 in array [COMPSIZE(numPaths,transformType)]
	category	NV_path_rendering
	version		1.1
	extension

CoverStrokePathInstancedNV(numPaths, pathNameType, paths, pathBase, coverMode, transformType, transformValues)
	return		void
	param		numPaths	SizeI in value
	param		pathNameType	PathElementType in value
	param		paths		PathElement in array [COMPSIZE(numPaths,pathNameType,paths)]
	param		pathBase	Path in value
	param		coverMode	PathCoverMode in value
	param		transformType	PathTransformType in value
	param		transformValues Float32 in array [COMPSIZE(numPaths,transformType)]
	category	NV_path_rendering
	version		1.1
	extension

# PATH QUERIES

GetPathParameterivNV(path, pname, value)
	return		void
	param		path		Path in value
	param		pname		PathParameter in value
	param		value		Int32 out array [4]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathParameterfvNV(path, pname, value)
	return		void
	param		path		Path in value
	param		pname		PathParameter in value
	param		value		Float32 out array [4]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathCommandsNV(path, commands)
	return		void
	param		path		Path in value
	param		commands	PathCommand out array [COMPSIZE(path)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathCoordsNV(path, coords)
	return		void
	param		path		Path in value
	param		coords		Float32 out array [COMPSIZE(path)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathDashArrayNV(path, dashArray)
	return		void
	param		path		Path in value
	param		dashArray	Float32 out array [COMPSIZE(path)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathMetricsNV(metricQueryMask, numPaths, pathNameType, paths, pathBase, stride, metrics)
	return		void
	param		metricQueryMask PathMetricMask in value
	param		numPaths	SizeI in value
	param		pathNameType	PathElementType in value
	param		paths		PathElement in array [COMPSIZE(numPaths,pathNameType,paths)]
	param		pathBase	Path in value
	param		stride		SizeI in value
	param		metrics		Float32 out array [COMPSIZE(metricQueryMask,numPaths,stride)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathMetricRangeNV(metricQueryMask, firstPathName, numPaths, stride, metrics)
	return		void
	param		metricQueryMask PathMetricMask in value
	param		firstPathName	Path in value
	param		numPaths	SizeI in value
	param		stride		SizeI in value
	param		metrics		Float32 out array [COMPSIZE(metricQueryMask,numPaths,stride)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathSpacingNV(pathListMode, numPaths, pathNameType, paths, pathBase, advanceScale, kerningScale, transformType, returnedSpacing)
	return		void
	param		pathListMode	PathListMode in value
	param		numPaths	SizeI in value
	param		pathNameType	PathElementType in value
	param		paths		PathElement in array [COMPSIZE(numPaths,pathNameType,paths)]
	param		pathBase	Path in value
	param		advanceScale	Float32 in value
	param		kerningScale	Float32 in value
	param		transformType	PathTransformType in value
	param		returnedSpacing Float32 out array [COMPSIZE(pathListMode,numPaths)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathColorGenivNV(color, pname, value)
	return		void
	param		color		PathColor in value
	param		pname		PathGenMode in value
	param		value		Int32 out array [COMPSIZE(pname)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathColorGenfvNV(color, pname, value)
	return		void
	param		color		PathColor in value
	param		pname		PathGenMode in value
	param		value		Float32 out array [COMPSIZE(pname)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathTexGenivNV(texCoordSet, pname, value)
	return		void
	param		texCoordSet	TextureUnit in value
	param		pname		PathGenMode in value
	param		value		Int32 out array [COMPSIZE(pname)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathTexGenfvNV(texCoordSet, pname, value)
	return		void
	param		texCoordSet	TextureUnit in value
	param		pname		PathGenMode in value
	param		value		Float32 out array [COMPSIZE(pname)]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

IsPointInFillPathNV(path, mask, x, y)
	return		Boolean
	param		path		Path in value
	param		mask		MaskedStencilValue in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

IsPointInStrokePathNV(path, x, y)
	return		Boolean
	param		path		Path in value
	param		x		Float32 in value
	param		y		Float32 in value
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

GetPathLengthNV(path, startSegment, numSegments)
	return		Float32
	param		path		Path in value
	param		startSegment	SizeI in value
	param		numSegments	SizeI in value
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

PointAlongPathNV(path, startSegment, numSegments, distance, x, y, tangentX, tangentY)
	return		Boolean
	param		path		Path in value
	param		startSegment	SizeI in value
	param		numSegments	SizeI in value
	param		distance	Float32 in value
	param		x		Float32 out array [1]
	param		y		Float32 out array [1]
	param		tangentX	Float32 out array [1]
	param		tangentY	Float32 out array [1]
	category	NV_path_rendering
	dlflags		notlistable
	version		1.1
	extension

###############################################################################
#
# Extension #411
# AMD_pinned_memory commands
#
###############################################################################

# (none)
newcategory: AMD_pinned_memory

###############################################################################
#
# Extension #412 - WGL_NV_DX_interop2
#
###############################################################################

###############################################################################
#
# Extension #413 - AMD_stencil_operation_extended
#
###############################################################################

StencilOpValueAMD(face, value)
	return		void
	param		face		StencilFaceDirection in value
	param		value		UInt32 in value
	category	AMD_stencil_operation_extended
	version		1.2
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #414 - GLX_EXT_swap_control_tear
# Extension #415 - WGL_EXT_swap_control_tear
#
###############################################################################

###############################################################################
#
# Extension #416
# AMD_vertex_shader_viewport_index commands
#
###############################################################################

# (none)
newcategory: AMD_vertex_shader_viewport_index

###############################################################################
#
# Extension #417
# AMD_vertex_shader_layer commands
#
###############################################################################

# (none)
newcategory: AMD_vertex_shader_layer

###############################################################################
#
# Extension #418
# NV_bindless_texture commands
#
###############################################################################

GetTextureHandleNV(texture)
	return		UInt64
	param		texture		UInt32 in value
	category	NV_bindless_texture
	dlflags		notlistable
	version		4.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

GetTextureSamplerHandleNV(texture, sampler)
	return		UInt64
	param		texture		UInt32 in value
	param		sampler		UInt32 in value
	category	NV_bindless_texture
	dlflags		notlistable
	version		4.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

MakeTextureHandleResidentNV(handle)
	return		void
	param		handle		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MakeTextureHandleNonResidentNV(handle)
	return		void
	param		handle		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

GetImageHandleNV(texture, level, layered, layer, format)
	return		UInt64
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		layered		Boolean in value
	param		layer		Int32 in value
	param		format		GLenum in value
	category	NV_bindless_texture
	dlflags		notlistable
	version		4.0
	extension
	glxsingle	?
	glxflags	ignore
	offset		?

MakeImageHandleResidentNV(handle, access)
	return		void
	param		handle		UInt64 in value
	param		access		GLenum in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MakeImageHandleNonResidentNV(handle)
	return		void
	param		handle		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformHandleui64NV(location, value)
	return		void
	param		location	Int32 in value
	param		value		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UniformHandleui64vNV(location, count, value)
	return		void
	param		location	Int32 in value
	param		count		SizeI in value
	param		value		UInt64 in array [count]
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformHandleui64NV(program, location, value)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		value		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

ProgramUniformHandleui64vNV(program, location, count, values)
	return		void
	param		program		UInt32 in value
	param		location	Int32 in value
	param		count		SizeI in value
	param		values		UInt64 in array [count]
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsTextureHandleResidentNV(handle)
	return		Boolean
	param		handle		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

IsImageHandleResidentNV(handle)
	return		Boolean
	param		handle		UInt64 in value
	category	NV_bindless_texture
	version		4.0
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #419
# NV_shader_atomic_float commands
#
###############################################################################

# (none)
newcategory: NV_shader_atomic_float

###############################################################################
#
# Extension #420
# AMD_query_buffer_object commands
#
###############################################################################

# (none)
newcategory: AMD_query_buffer_object

###############################################################################

###############################################################################
#
# Extension #421
# NV_compute_program5 commands
#
###############################################################################

# (none)
newcategory: NV_compute_program5

###############################################################################
#
# Extension #422
# NV_shader_storage_buffer_object commands
#
###############################################################################

# (none)
newcategory: NV_shader_storage_buffer_object

###############################################################################
#
# Extension #423
# NV_shader_atomic_counters commands
#
###############################################################################

# (none)
newcategory: NV_shader_atomic_counters

###############################################################################
#
# Extension #424
# NV_deep_texture3D commands
#
###############################################################################

# (none)
newcategory: NV_deep_texture3D

###############################################################################
#
# Extension #425
# NVX_conditional_render enum:
#
###############################################################################

BeginConditionalRenderNVX(id)
	return		void
	param		id		UInt32 in value
	category	NVX_conditional_render
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

EndConditionalRenderNVX()
	return		void
	category	NVX_conditional_render
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #426
# AMD_sparse_texture commands
#
###############################################################################

TexStorageSparseAMD(target, internalFormat, width, height, depth, layers, flags)
	return		void
	param		target		GLenum in value
	param		internalFormat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		layers		SizeI in value
	param		flags		GLbitfield in value
	category	AMD_sparse_texture
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

TextureStorageSparseAMD(texture, target, internalFormat, width, height, depth, layers, flags)
	return		void
	param		texture		UInt32 in value
	param		target		GLenum in value
	param		internalFormat	GLenum in value
	param		width		SizeI in value
	param		height		SizeI in value
	param		depth		SizeI in value
	param		layers		SizeI in value
	param		flags		GLbitfield in value
	category	AMD_sparse_texture
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #427 - GLX_EXT_buffer_age
#
###############################################################################

###############################################################################
#
# Extension #428
# AMD_shader_trinary_minmax commands
#
###############################################################################

# (none)
newcategory: AMD_shader_trinary_minmax

###############################################################################
#
# Extension #429
# INTEL_map_texture commands
#
###############################################################################

SyncTextureINTEL(texture)
	return		void
	param		texture		UInt32 in value
	category	INTEL_map_texture
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

UnmapTexture2DINTEL(texture, level)
	return		void
	param		texture		UInt32 in value
	param		level		Int32 in value
	category	INTEL_map_texture
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

MapTexture2DINTEL(texture, level, access, stride, layout)
	return		VoidPointer
	param		texture		UInt32 in value
	param		level		Int32 in value
	param		access		GLbitfield in value
	param		stride		Int32 in array [1]
	param		layout		GLenum in array [1]
	category	INTEL_map_texture
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

###############################################################################
#
# Extension #430
# NV_draw_texture commands
#
###############################################################################

DrawTextureNV(texture, sampler, x0, y0, x1, y1, z, s0, t0, s1, t1)
	return		void
	param		texture		UInt32 in value
	param		sampler		UInt32 in value
	param		x0		Float32 in value
	param		y0		Float32 in value
	param		x1		Float32 in value
	param		y1		Float32 in value
	param		z		Float32 in value
	param		s0		Float32 in value
	param		t0		Float32 in value
	param		s1		Float32 in value
	param		t1		Float32 in value
	category	NV_draw_texture
	version		4.3
	extension
	glxropcode	?
	glxflags	ignore
	offset		?

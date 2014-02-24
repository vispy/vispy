/*
 *   Project: SIFT: An algorithm for image alignement
 *            kernel for maximum and minimum calculation
 *
 *
 *   Copyright (C) 2013 European Synchrotron Radiation Facility
 *                           Grenoble, France
 *   All rights reserved.
 *
 *   Principal authors: J. Kieffer (kieffer@esrf.fr)
 *   Last revision: 21/06/2013
 *
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 */


#ifndef WORKGROUP_SIZE
	#define WORKGROUP_SIZE 1024
#endif


#define REDUCE(a, b) ((float2)(fmax(a.x,b.x),fmin(a.y,b.y)))
#define READ_AND_MAP(i) ((float2)(data[i],data[i]))

/**
 * \brief max_min_global_stage1: Look for the maximum an the minimum of an array. stage1
 *
 * optimal workgroup size: 2^n greater than sqrt(SIZE), limited to 512
 * optimal total item size:  (workgroup size)^2
 * if SIZE >total item size: adjust seq_count.
 *
 * @param data:       Float pointer to global memory storing the vector of data.
 * @param out:    	  Float2 pointer to global memory storing the temporary results (workgroup size)
 * @param seq_count:  how many blocksize each thread should read
 * @param SIZE:		  size of the
 *
**/


__kernel void max_min_global_stage1(
		__global const float *data,
		__global float2 *out,
		unsigned int SIZE){

    __local volatile float2 ldata[WORKGROUP_SIZE];
    unsigned int group_size =  min((unsigned int) get_local_size(0), (unsigned int) WORKGROUP_SIZE);
    unsigned int lid = get_local_id(0);
    float2 acc;
    unsigned int big_block = group_size * get_num_groups(0);
    unsigned int i =  lid + group_size * get_group_id(0); //get_global_id(0);

    if (lid<SIZE)
    	acc = READ_AND_MAP(lid);
    else
    	acc = READ_AND_MAP(0);
    while (i<SIZE){
      acc = REDUCE(acc, READ_AND_MAP(i));
      i += big_block; //get_global_size(0);
    }
    ldata[lid] = acc;
    barrier(CLK_LOCAL_MEM_FENCE);

    if ((lid<group_size) && (lid < 512) && ((lid + 512)<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 512]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 256) && ((lid + 256)<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 256]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 128) && ((lid + 128)<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 128]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 64 ) && ((lid + 64 )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 64 ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 32 ) && ((lid + 32 )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 32 ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 16 ) && ((lid + 16 )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 16 ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 8  ) && ((lid + 8  )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 8  ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);

    if ((lid<group_size) && (lid < 4  ) && ((lid + 4  )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 4  ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 2  ) && ((lid + 2  )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 2  ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((lid<group_size) && (lid < 1  ) && ((lid + 1  )<group_size)){
    	ldata[lid] = REDUCE(ldata[lid], ldata[lid + 1  ]);
    }
    barrier(CLK_LOCAL_MEM_FENCE);

  	out[get_group_id(0)] = ldata[0];
}


/**
 * \brief global_max_min: Look for the maximum an the minimum of an array.
 *
 *
 *
 * @param data2:      Float2 pointer to global memory storing the vector of pre-reduced data (workgroup size).
 * @param maximum:    Float pointer to global memory storing the maximum value
 * @param minumum:    Float pointer to global memory storing the minimum value
 *
**/

__kernel void max_min_global_stage2(
		__global const float2 *data2,
		__global float *maximum,
		__global float *minimum){

	__local float2 ldata[WORKGROUP_SIZE];
    unsigned int lid = get_local_id(0);
    unsigned int group_size =  min((unsigned int) get_local_size(0), (unsigned int) WORKGROUP_SIZE);
    float2 acc = (float2)(-1.0f, -1.0f);
    if (lid<=group_size){
    	ldata[lid] = data2[lid];
    }else{
    	ldata[lid] = acc;
    }
	barrier(CLK_LOCAL_MEM_FENCE);

	if ((lid<group_size) && (lid < 512) && ((lid + 512)<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 512]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 256) && ((lid + 256)<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 256]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 128) && ((lid + 128)<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 128]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 64 ) && ((lid + 64 )<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 64 ]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 32 ) && ((lid + 32 )<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 32 ]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 16 ) && ((lid + 16 )<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 16 ]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 8  ) && ((lid + 8  )<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 8  ]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 4  ) && ((lid + 4  )<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 4  ]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);
	if ((lid<group_size) && (lid < 2  ) && ((lid + 2  )<group_size)){
		ldata[lid] = REDUCE(ldata[lid], ldata[lid + 2  ]);
	}
	barrier(CLK_LOCAL_MEM_FENCE);

	if (lid == 0  ){
		if ( 1 < group_size){
			acc = REDUCE(ldata[0], ldata[1]);
		}else{
			acc = ldata[0];
		}
		maximum[0] = acc.x;
		minimum[0] = acc.y;
	}
}

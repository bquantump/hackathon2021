/* -*- c++ -*- */
/*
 * Copyright 2005,2010,2012 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "fft_filter_ccc_impl.h"
#include <gnuradio/io_signature.h>

#include <assert.h>
#include <cmath>
#include <stdexcept>

namespace gr {
namespace filter {

fft_filter_ccc::sptr
fft_filter_ccc::make(int decimation, const std::vector<gr_complex>& taps, int nthreads)
{
    return gnuradio::make_block_sptr<fft_filter_ccc_impl>(decimation, taps, nthreads);
}

fft_filter_ccc_impl::fft_filter_ccc_impl(int decimation,
                                         const std::vector<gr_complex>& taps,
                                         int nthreads)
    : sync_decimator("fft_filter_ccc",
                     io_signature::make(1, 1, sizeof(gr_complex)),
                     io_signature::make(1, 1, sizeof(gr_complex)),
                     decimation),
      d_updated(false),
      d_filter(decimation, taps, nthreads)
{
    d_new_taps = taps;
    d_nsamples = d_filter.set_taps(taps);
    set_output_multiple(d_nsamples);
    message_port_register_in(pmt::mp("taps"));
    this->set_msg_handler(pmt::mp("taps"),
                          [this](pmt::pmt_t msg) { this->handle_set_taps(msg); });
}

void fft_filter_ccc_impl::set_taps(const std::vector<gr_complex>& taps)
{
    d_new_taps = taps;
    d_updated = true;
}

void fft_filter_ccc_impl::handle_set_taps(pmt::pmt_t msg)
{   
    printf("in handle taps\n");
    printf("pmt::is_dict(msg) %d\n", pmt::is_dict(msg));
    printf("pmt::dict_has_key(msg, pmt::intern(\"taps\")) %d]\n", pmt::dict_has_key(msg, pmt::intern("taps")));
    if (pmt::is_dict(msg) && pmt::dict_has_key(msg, pmt::intern("taps"))) {
        printf("got past first check\n");
        pmt::pmt_t x = pmt::dict_ref(msg, pmt::intern("taps"), pmt::PMT_NIL);
        printf("is null %d\n", pmt::is_null(x));
        if (pmt::is_f32vector(x)) {
  
            //auto taps = pmt::c32vector_elements(x);
            printf("is f32\n");
            //set_taps(taps);
        }
        else if (pmt::is_f64vector(x))
        {
            printf("is f64\n");
        }
        else if (pmt::is_c32vector(x))
        {
                        printf("is c32\n");
            auto taps = pmt::c32vector_elements(x);
            set_taps(taps);
        }
        else if (pmt::is_c64vector(x))
        {
            printf("is c64\n");
        }
    
    }
}

std::vector<gr_complex> fft_filter_ccc_impl::taps() const { return d_new_taps; }

void fft_filter_ccc_impl::set_nthreads(int n) { d_filter.set_nthreads(n); }

int fft_filter_ccc_impl::nthreads() const { return d_filter.nthreads(); }

int fft_filter_ccc_impl::work(int noutput_items,
                              gr_vector_const_void_star& input_items,
                              gr_vector_void_star& output_items)
{
    const gr_complex* in = (const gr_complex*)input_items[0];
    gr_complex* out = (gr_complex*)output_items[0];

    if (d_updated) {
        d_nsamples = d_filter.set_taps(d_new_taps);
        d_updated = false;
        set_output_multiple(d_nsamples);
        return 0; // output multiple may have changed
    }

    d_filter.filter(noutput_items, in, out);

    return noutput_items;
}

} /* namespace filter */
} /* namespace gr */

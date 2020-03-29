

typedef struct FLIF_IMAGE FLIF_IMAGE;
typedef struct FLIF_ENCODER FLIF_ENCODER;
typedef struct FLIF_DECODER FLIF_DECODER;
typedef struct FLIF_INFO FLIF_INFO;
typedef uint32_t (*callback_t)(uint32_t quality, int64_t bytes_read, uint8_t decode_over, void *user_data, void *context);

FLIF_IMAGE*    flif_create_image(uint32_t width, uint32_t height);
FLIF_IMAGE*    flif_create_image_RGB(uint32_t width, uint32_t height);
FLIF_IMAGE*    flif_create_image_GRAY(uint32_t width, uint32_t height);
FLIF_IMAGE*    flif_create_image_GRAY16(uint32_t width, uint32_t height);
FLIF_IMAGE*    flif_create_image_PALETTE(uint32_t width, uint32_t height);
FLIF_IMAGE*    flif_create_image_HDR(uint32_t width, uint32_t height);
FLIF_IMAGE*    flif_import_image_RGBA(uint32_t width, uint32_t height, const void* rgba, uint32_t rgba_stride);
FLIF_IMAGE*    flif_import_image_RGB(uint32_t width, uint32_t height, const void* rgb, uint32_t rgb_stride);
FLIF_IMAGE*    flif_import_image_GRAY(uint32_t width, uint32_t height, const void* gray, uint32_t gray_stride);
FLIF_IMAGE*    flif_import_image_GRAY16(uint32_t width, uint32_t height, const void* gray, uint32_t gray_stride);
FLIF_IMAGE*    flif_import_image_PALETTE(uint32_t width, uint32_t height, const void* gray, uint32_t gray_stride);
FLIF_IMAGE*    flif_decoder_get_image(FLIF_DECODER* decoder, size_t index);

FLIF_DECODER*    flif_create_decoder();

FLIF_ENCODER*    flif_create_encoder();

FLIF_INFO*    flif_read_info_from_memory(const void* buffer, size_t buffer_size_bytes);

int32_t    flif_decoder_decode_file(FLIF_DECODER* decoder, const char* filename);
int32_t    flif_decoder_decode_memory(FLIF_DECODER* decoder, const void* buffer, size_t buffer_size_bytes);
int32_t    flif_decoder_decode_filepointer(FLIF_DECODER* decoder, FILE *filepointer, const char *filename);
int32_t    flif_decoder_num_loops(FLIF_DECODER* decoder);
int32_t    flif_abort_decoder(FLIF_DECODER* decoder);
int32_t    flif_encoder_encode_file(FLIF_ENCODER* encoder, const char* filename);
int32_t    flif_encoder_encode_memory(FLIF_ENCODER* encoder, void** buffer, size_t* buffer_size_bytes);

uint32_t    flif_image_get_palette_size(FLIF_IMAGE* image);
uint32_t    flif_image_get_frame_delay(FLIF_IMAGE* image);
uint32_t    flif_image_get_width(FLIF_IMAGE* image);
uint32_t    flif_image_get_height(FLIF_IMAGE* image);
uint32_t    flif_info_get_width(FLIF_INFO* info);
uint32_t    flif_info_get_height(FLIF_INFO* info);

uint8_t     flif_image_get_nb_channels(FLIF_IMAGE* image);
uint8_t     flif_image_get_depth(FLIF_IMAGE* image);
uint8_t    flif_image_get_metadata(FLIF_IMAGE* image, const char* chunkname, unsigned char** data, size_t* length);
uint8_t     flif_info_get_nb_channels(FLIF_INFO* info);
uint8_t     flif_info_get_depth(FLIF_INFO* info);

size_t      flif_info_num_images(FLIF_INFO* info);
size_t    flif_decoder_num_images(FLIF_DECODER* decoder);

void    flif_destroy_image(FLIF_IMAGE* image);
void    flif_image_get_palette(FLIF_IMAGE* image, void* buffer);
void    flif_image_set_palette(FLIF_IMAGE* image, const void* buffer, uint32_t palette_size);
void    flif_image_set_frame_delay(FLIF_IMAGE* image, uint32_t delay);
void    flif_image_set_metadata(FLIF_IMAGE* image, const char* chunkname, const unsigned char* data, size_t length);
void    flif_image_free_metadata(FLIF_IMAGE* image, unsigned char* data);
void    flif_image_write_row_PALETTE8(FLIF_IMAGE* image, uint32_t row, const void* buffer, size_t buffer_size_bytes);
void    flif_image_read_row_PALETTE8(FLIF_IMAGE* image, uint32_t row, void* buffer, size_t buffer_size_bytes);
void    flif_image_write_row_GRAY8(FLIF_IMAGE* image, uint32_t row, const void* buffer, size_t buffer_size_bytes);
void    flif_image_read_row_GRAY8(FLIF_IMAGE* image, uint32_t row, void* buffer, size_t buffer_size_bytes);
void    flif_image_write_row_GRAY16(FLIF_IMAGE* image, uint32_t row, const void* buffer, size_t buffer_size_bytes);
void    flif_image_read_row_GRAY16(FLIF_IMAGE* image, uint32_t row, void* buffer, size_t buffer_size_bytes);
void    flif_image_write_row_RGBA8(FLIF_IMAGE* image, uint32_t row, const void* buffer, size_t buffer_size_bytes);
void    flif_image_read_row_RGBA8(FLIF_IMAGE* image, uint32_t row, void* buffer, size_t buffer_size_bytes);
void    flif_image_write_row_RGBA16(FLIF_IMAGE* image, uint32_t row, const void* buffer, size_t buffer_size_bytes);
void    flif_image_read_row_RGBA16(FLIF_IMAGE* image, uint32_t row, void* buffer, size_t buffer_size_bytes);
void    flif_free_memory(void* buffer);
void    flif_decoder_generate_preview(void *context);
void    flif_destroy_decoder(FLIF_DECODER* decoder);
void    flif_decoder_set_crc_check(FLIF_DECODER* decoder, int32_t crc_check);
void    flif_decoder_set_quality(FLIF_DECODER* decoder, int32_t quality);
void    flif_decoder_set_scale(FLIF_DECODER* decoder, uint32_t scale);
void    flif_decoder_set_resize(FLIF_DECODER* decoder, uint32_t width, uint32_t height);
void    flif_decoder_set_fit(FLIF_DECODER* decoder, uint32_t width, uint32_t height);
void    flif_decoder_set_callback(FLIF_DECODER* decoder, callback_t callback, void *user_data);
void    flif_decoder_set_first_callback_quality(FLIF_DECODER* decoder, int32_t quality);
void    flif_destroy_info(FLIF_INFO* info);
void    flif_encoder_add_image(FLIF_ENCODER* encoder, FLIF_IMAGE* image);
void    flif_encoder_add_image_move(FLIF_ENCODER* encoder, FLIF_IMAGE* image);
void    flif_destroy_encoder(FLIF_ENCODER* encoder);
void    flif_encoder_set_interlaced(FLIF_ENCODER* encoder, uint32_t interlaced);
void    flif_encoder_set_learn_repeat(FLIF_ENCODER* encoder, uint32_t learn_repeats);
void    flif_encoder_set_auto_color_buckets(FLIF_ENCODER* encoder, uint32_t acb);
void    flif_encoder_set_palette_size(FLIF_ENCODER* encoder, int32_t palette_size);
void    flif_encoder_set_lookback(FLIF_ENCODER* encoder, int32_t lookback);
void    flif_encoder_set_divisor(FLIF_ENCODER* encoder, int32_t divisor);
void    flif_encoder_set_min_size(FLIF_ENCODER* encoder, int32_t min_size);
void    flif_encoder_set_split_threshold(FLIF_ENCODER* encoder, int32_t threshold);
void    flif_encoder_set_alpha_zero(FLIF_ENCODER* encoder, int32_t lossless);
void    flif_encoder_set_alpha_zero_lossless(FLIF_ENCODER* encoder);
void    flif_encoder_set_chance_cutoff(FLIF_ENCODER* encoder, int32_t cutoff);
void    flif_encoder_set_chance_alpha(FLIF_ENCODER* encoder, int32_t alpha);
void    flif_encoder_set_crc_check(FLIF_ENCODER* encoder, uint32_t crc_check);
void    flif_encoder_set_channel_compact(FLIF_ENCODER* encoder, uint32_t plc);
void    flif_encoder_set_ycocg(FLIF_ENCODER* encoder, uint32_t ycocg);
void    flif_encoder_set_frame_shape(FLIF_ENCODER* encoder, uint32_t frs);
void    flif_encoder_set_lossy(FLIF_ENCODER* encoder, int32_t loss);
void    flif_image_read_into_GRAY8(FLIF_IMAGE *image, void *buffer, size_t buffer_size);
void    flif_image_read_into_RGBA8(FLIF_IMAGE *image, void *buffer, size_t buffer_size);
void    flif_image_read_into_RGB8(FLIF_IMAGE *image, void *buffer, size_t buffer_size);
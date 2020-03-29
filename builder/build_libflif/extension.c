
#include <flif.h>
#include <Python.h>
#include <windows.h>

/*
uint32_t flif_python_callback(uint32_t quality, int64_t bytes_read, uint8_t decode_over, void *user_data, void *context)
{
    PyObject *py_callback = user_data;

    if (!user_data)
    {
        PyErr_SetString(PyExc_ValueError, "user_data cannot be NULL for python callbacks");
        return 0;
    }

    // TODO
} */

void flif_image_read_into_GRAY8(FLIF_IMAGE *image, void *buffer, size_t buffer_size)
{
    uint32_t rows = flif_image_get_height(image);
    uint32_t columns = flif_image_get_width(image);

    for (uint32_t row = 0; row < rows && (row + 1) * columns <= buffer_size; ++row)
    {
        flif_image_read_row_GRAY8(image, row, (char *)buffer + row * columns, columns);
    }
}

void flif_image_read_into_RGBA8(FLIF_IMAGE *image, void *buffer, size_t buffer_size)
{
    uint32_t rows = flif_image_get_height(image);
    uint32_t columns = flif_image_get_width(image);

    for (uint32_t row = 0; row < rows && (row + 1) * columns * 4 <= buffer_size; ++row)
    {
        flif_image_read_row_RGBA8(image, row, (char *)buffer + row * columns * 4, columns * 4);
    }
}

void flif_image_read_into_RGB8(FLIF_IMAGE *image, void *buffer, size_t buffer_size)
{
    uint32_t rows = flif_image_get_height(image);
    uint32_t columns = flif_image_get_width(image);
    uint32_t row;

    for (row = 0; row < rows && row * columns * 3 + columns * 4 <= buffer_size; ++row)
    {
        // Read RGBA8
        uint8_t *row_buf = (uint8_t *)buffer + row * columns * 3;
        flif_image_read_row_RGBA8(image, row, row_buf, columns * 4);
        // Remove Alpha channel
        for (uint32_t col = 1; col < columns; ++col)
        {
            row_buf[col * 3] = row_buf[col * 4];
            row_buf[col * 3 + 1] = row_buf[col * 4 + 1];
            row_buf[col * 3 + 2] = row_buf[col * 4 + 2];
        }
    }

    // Last row
    if (row < rows && buffer_size >= (row + 1) * columns * 3)
    {
        uint8_t *lastrow_buf =  malloc(columns * 4);
        uint8_t *row_buf = malloc((uint8_t *)buffer + row * columns * 3);
        flif_image_read_row_RGBA8(image, row, lastrow_buf, columns * 4);

        for (uint32_t col = 0; col < columns; ++col)
        {
            row_buf[col * 3] = lastrow_buf[col * 4];
            row_buf[col * 3 + 1] = lastrow_buf[col * 4 + 1];
            row_buf[col * 3 + 2] = lastrow_buf[col * 4 + 2];
        }
    }
}
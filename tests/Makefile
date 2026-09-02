CC ?= cc
CFLAGS ?= -std=c99 -Wall -Wextra -Werror -pedantic
BUILD_DIR ?= build

.PHONY: all check clean

all: $(BUILD_DIR)/test_fault_block_device $(BUILD_DIR)/test_crash_harness

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/test_fault_block_device: fault_block_device.c fault_block_device.h test_fault_block_device.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) fault_block_device.c test_fault_block_device.c -o $@

$(BUILD_DIR)/test_crash_harness: fault_block_device.c fault_block_device.h crash_harness.c crash_harness.h test_crash_harness.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) fault_block_device.c crash_harness.c test_crash_harness.c -o $@

check: all
	$(BUILD_DIR)/test_fault_block_device
	$(BUILD_DIR)/test_crash_harness

clean:
	rm -f $(BUILD_DIR)/test_fault_block_device $(BUILD_DIR)/test_crash_harness

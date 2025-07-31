# Makefile for LatticeSound 2D Engine
# Compiles the C components of the LatticeSound system

CC = gcc
CFLAGS = -pthread -Wall -O2
LDFLAGS = -lgsl -lgslcblas -lm

# Detect OS and set GSL paths accordingly
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    # macOS - try Homebrew paths
    ifeq ($(shell test -d /opt/homebrew/Cellar/gsl && echo "exists"),exists)
        CFLAGS += -I/opt/homebrew/Cellar/gsl/2.8/include
        LDFLAGS += -L/opt/homebrew/Cellar/gsl/2.8/lib
    else ifeq ($(shell test -d /usr/local/Cellar/gsl && echo "exists"),exists)
        CFLAGS += -I/usr/local/Cellar/gsl/2.8/include
        LDFLAGS += -L/usr/local/Cellar/gsl/2.8/lib
    endif
else ifeq ($(UNAME_S),Linux)
    # Linux - use pkg-config if available, otherwise use standard paths
    ifeq ($(shell pkg-config --exists gsl && echo "exists"),exists)
        CFLAGS += $(shell pkg-config --cflags gsl)
        LDFLAGS += $(shell pkg-config --libs gsl)
    endif
endif

# Source files
SOURCES = C_Lattice.c h_shape.c C_Lattice_Worker.c C_Lattice_dif_sys.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = C_Lattice

# Default target
all: $(TARGET)

# Compile the main executable
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Compile object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(OBJECTS) $(TARGET)

# Install (copy to parent directory for compatibility)
install: $(TARGET)
	cp $(TARGET) ../

# Check GSL installation
check-gsl:
	@echo "Checking GSL installation..."
	@echo "OS: $(UNAME_S)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo "LDFLAGS: $(LDFLAGS)"
	@if pkg-config --exists gsl; then \
		echo "GSL found via pkg-config"; \
	else \
		echo "GSL not found via pkg-config"; \
	fi

# Help
help:
	@echo "Available targets:"
	@echo "  all        - Build the C_Lattice executable (default)"
	@echo "  clean      - Remove build files"
	@echo "  install    - Build and copy executable to parent directory"
	@echo "  check-gsl  - Check GSL installation status"
	@echo "  help       - Show this help message"

.PHONY: all clean install check-gsl help 
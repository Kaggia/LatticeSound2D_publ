# Makefile for LatticeSound 2D Engine
# Compiles the C components of the LatticeSound system

CC = gcc
CFLAGS = -pthread -I/opt/homebrew/Cellar/gsl/2.8/include
LDFLAGS = -L/opt/homebrew/Cellar/gsl/2.8/lib -lgsl -lgslcblas -lm

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

# Help
help:
	@echo "Available targets:"
	@echo "  all      - Build the C_Lattice executable (default)"
	@echo "  clean    - Remove build files"
	@echo "  install  - Build and copy executable to parent directory"
	@echo "  help     - Show this help message"

.PHONY: all clean install help 
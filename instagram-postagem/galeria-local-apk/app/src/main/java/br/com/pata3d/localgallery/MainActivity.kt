package br.com.pata3d.localgallery

import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CloudUpload
import androidx.compose.material.icons.rounded.Folder
import androidx.compose.material.icons.rounded.PlayCircle
import androidx.compose.material.icons.rounded.Refresh
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ElevatedCard
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import coil.compose.AsyncImage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.net.URLEncoder
import java.util.UUID

data class FolderItem(
    val name: String,
    val relativePath: String,
    val mediaCount: Int,
)

data class MediaItem(
    val name: String,
    val relativePath: String,
    val folder: String,
    val type: String,
    val sizeBytes: Long,
    val mediaUrl: String,
)

data class GalleryUiState(
    val baseUrl: String = "",
    val currentFolder: String = "",
    val folders: List<FolderItem> = emptyList(),
    val items: List<MediaItem> = emptyList(),
    val isLoading: Boolean = false,
    val isUploading: Boolean = false,
    val message: String? = null,
    val error: String? = null,
)

class ServerPreferences(context: Context) {
    private val prefs = context.getSharedPreferences("pata3d_local_gallery", Context.MODE_PRIVATE)

    fun loadBaseUrl(): String = prefs.getString("base_url", "http://192.168.50.46:8765") ?: "http://192.168.50.46:8765"

    fun saveBaseUrl(url: String) {
        prefs.edit().putString("base_url", url).apply()
    }
}

class LocalGalleryRepository(
    private val context: Context,
) {
    private val client = OkHttpClient()

    fun fetchFolders(baseUrl: String): List<FolderItem> {
        val request = Request.Builder()
            .url(baseUrl.trimEnd('/') + "/api/folders")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error("Falha ao buscar pastas: ${response.code}")
            val body = response.body?.string().orEmpty()
            val json = JSONObject(body)
            val foldersArray = json.getJSONArray("folders")
            return buildList {
                for (index in 0 until foldersArray.length()) {
                    val item = foldersArray.getJSONObject(index)
                    add(
                        FolderItem(
                            name = item.getString("name"),
                            relativePath = item.getString("relativePath"),
                            mediaCount = item.getInt("mediaCount"),
                        )
                    )
                }
            }
        }
    }

    fun fetchMedia(baseUrl: String, folder: String): List<MediaItem> {
        val encodedFolder = URLEncoder.encode(folder, Charsets.UTF_8.name())
        val request = Request.Builder()
            .url(baseUrl.trimEnd('/') + "/api/media?folder=$encodedFolder")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error("Falha ao buscar galeria: ${response.code}")
            val body = response.body?.string().orEmpty()
            val json = JSONObject(body)
            val itemsArray = json.getJSONArray("items")
            return buildList {
                for (index in 0 until itemsArray.length()) {
                    val item = itemsArray.getJSONObject(index)
                    add(
                        MediaItem(
                            name = item.getString("name"),
                            relativePath = item.getString("relativePath"),
                            folder = item.getString("folder"),
                            type = item.getString("type"),
                            sizeBytes = item.getLong("sizeBytes"),
                            mediaUrl = item.getString("mediaUrl"),
                        )
                    )
                }
            }
        }
    }

    fun uploadFiles(baseUrl: String, folder: String, uris: List<Uri>): String {
        val resolver = context.contentResolver
        val bodyBuilder = MultipartBody.Builder().setType(MultipartBody.FORM)
        bodyBuilder.addFormDataPart("current_folder", folder)
        bodyBuilder.addFormDataPart("target_folder", folder)
        bodyBuilder.addFormDataPart("new_folder", "")

        var attachedCount = 0
        uris.forEach { uri ->
            val mimeType = resolver.getType(uri) ?: "application/octet-stream"
            val extension = when {
                mimeType.startsWith("image/") -> ".jpg"
                mimeType.startsWith("video/") -> ".mp4"
                else -> ""
            }
            val fileName = queryDisplayName(context, uri) ?: "arquivo_${UUID.randomUUID()}$extension"
            val tempFile = copyUriToCacheFile(context, uri, fileName)
            bodyBuilder.addFormDataPart(
                "files",
                fileName,
                tempFile.asRequestBody(mimeType.toMediaTypeOrNull())
            )
            attachedCount += 1
        }

        if (attachedCount == 0) error("Nenhum arquivo válido selecionado.")

        val request = Request.Builder()
            .url(baseUrl.trimEnd('/') + "/upload")
            .addHeader("Accept", "application/json")
            .post(bodyBuilder.build())
            .build()

        client.newCall(request).execute().use { response ->
            val body = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                val message = runCatching { JSONObject(body).optString("message") }.getOrNull()
                error(message ?: "Falha no upload: ${response.code}")
            }
            return JSONObject(body).optString("message", "Upload concluído.")
        }
    }

    private fun queryDisplayName(context: Context, uri: Uri): String? {
        context.contentResolver.query(uri, arrayOf(android.provider.OpenableColumns.DISPLAY_NAME), null, null, null)
            ?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val index = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                    if (index >= 0) return cursor.getString(index)
                }
            }
        return null
    }

    private fun copyUriToCacheFile(context: Context, uri: Uri, name: String): File {
        val safeName = name.replace(Regex("[^A-Za-z0-9._-]"), "_")
        val target = File(context.cacheDir, safeName)
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(target).use { output -> input.copyTo(output) }
        } ?: error("Não foi possível ler o arquivo selecionado.")
        return target
    }
}

class MainViewModel(
    private val repository: LocalGalleryRepository,
    private val prefs: ServerPreferences,
) : ViewModel() {
    private val _uiState = MutableStateFlow(GalleryUiState(baseUrl = prefs.loadBaseUrl()))
    val uiState: StateFlow<GalleryUiState> = _uiState.asStateFlow()

    init {
        refreshAll()
    }

    fun saveBaseUrl(url: String) {
        val normalized = url.trim().trimEnd('/')
        prefs.saveBaseUrl(normalized)
        _uiState.value = _uiState.value.copy(baseUrl = normalized)
        refreshAll()
    }

    fun selectFolder(relativePath: String) {
        _uiState.value = _uiState.value.copy(currentFolder = relativePath)
        refreshMedia()
    }

    fun clearMessage() {
        _uiState.value = _uiState.value.copy(message = null, error = null)
    }

    fun refreshAll() {
        viewModelScope.launch(Dispatchers.IO) {
            val current = _uiState.value
            _uiState.value = current.copy(isLoading = true, error = null, message = null)
            runCatching {
                val folders = repository.fetchFolders(current.baseUrl)
                val chosenFolder = current.currentFolder.ifBlank {
                    folders.firstOrNull { it.relativePath.isNotBlank() }?.relativePath.orEmpty()
                }
                val items = repository.fetchMedia(current.baseUrl, chosenFolder)
                _uiState.value = current.copy(
                    baseUrl = current.baseUrl,
                    folders = folders,
                    currentFolder = chosenFolder,
                    items = items,
                    isLoading = false,
                )
            }.onFailure { error ->
                _uiState.value = current.copy(
                    isLoading = false,
                    error = error.message ?: "Falha ao atualizar dados."
                )
            }
        }
    }

    fun refreshMedia() {
        viewModelScope.launch(Dispatchers.IO) {
            val current = _uiState.value
            _uiState.value = current.copy(isLoading = true, error = null, message = null)
            runCatching {
                val items = repository.fetchMedia(current.baseUrl, current.currentFolder)
                _uiState.value = current.copy(items = items, isLoading = false)
            }.onFailure { error ->
                _uiState.value = current.copy(
                    isLoading = false,
                    error = error.message ?: "Falha ao atualizar galeria."
                )
            }
        }
    }

    fun uploadSelected(uris: List<Uri>) {
        if (uris.isEmpty()) return
        viewModelScope.launch(Dispatchers.IO) {
            val current = _uiState.value
            _uiState.value = current.copy(isUploading = true, error = null, message = null)
            runCatching {
                val message = repository.uploadFiles(current.baseUrl, current.currentFolder, uris)
                val items = repository.fetchMedia(current.baseUrl, current.currentFolder)
                _uiState.value = current.copy(
                    items = items,
                    isUploading = false,
                    message = message
                )
            }.onFailure { error ->
                _uiState.value = current.copy(
                    isUploading = false,
                    error = error.message ?: "Falha ao enviar arquivos."
                )
            }
        }
    }
}

class MainViewModelFactory(
    private val context: Context,
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return MainViewModel(
                repository = LocalGalleryRepository(context),
                prefs = ServerPreferences(context),
            ) as T
        }
        throw IllegalArgumentException("ViewModel desconhecido")
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val factory = MainViewModelFactory(applicationContext)
        val viewModel = ViewModelProvider(this, factory)[MainViewModel::class.java]

        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFFFFFAF7)) {
                    GalleryApp(viewModel = viewModel)
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GalleryApp(viewModel: MainViewModel) {
    val state by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var serverUrlInput by rememberSaveable(state.baseUrl) { mutableStateOf(state.baseUrl) }

    val picker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenMultipleDocuments()
    ) { uris ->
        viewModel.uploadSelected(uris)
    }

    LaunchedEffect(state.message, state.error) {
        val text = state.message ?: state.error
        if (!text.isNullOrBlank()) {
            snackbarHostState.showSnackbar(text)
            viewModel.clearMessage()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        topBar = {
            TopAppBar(
                title = { Text("Galeria Local Pata3D") },
                actions = {
                    Button(onClick = { viewModel.refreshAll() }) {
                        Icon(Icons.Rounded.Refresh, contentDescription = null)
                        Spacer(modifier = Modifier.size(8.dp))
                        Text("Atualizar")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ElevatedCard(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(28.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            brush = Brush.verticalGradient(
                                listOf(Color(0xFFFFF4F7), Color(0xFFF6FBFF))
                            )
                        )
                        .padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Conecte no servidor do PC",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    OutlinedTextField(
                        value = serverUrlInput,
                        onValueChange = { serverUrlInput = it },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("IP do PC") },
                        placeholder = { Text("http://192.168.50.46:8765") },
                        singleLine = true
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Button(onClick = { viewModel.saveBaseUrl(serverUrlInput) }) {
                            Text("Salvar servidor")
                        }
                        Button(onClick = { picker.launch(arrayOf("image/*", "video/*")) }) {
                            Icon(Icons.Rounded.CloudUpload, contentDescription = null)
                            Spacer(modifier = Modifier.size(8.dp))
                            Text("Enviar mídia")
                        }
                    }
                    Text(
                        text = "Pasta atual: ${if (state.currentFolder.isBlank()) "raiz" else state.currentFolder}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color(0xFF6E5D5B)
                    )
                    if (state.isUploading) {
                        LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                    }
                }
            }

            Text(
                text = "Pastas",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )

            LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                items(state.folders, key = { it.relativePath + it.name }) { folder ->
                    val selected = folder.relativePath == state.currentFolder
                    AssistChip(
                        onClick = { viewModel.selectFolder(folder.relativePath) },
                        label = { Text("${folder.name} (${folder.mediaCount})") },
                        leadingIcon = {
                            Icon(
                                imageVector = Icons.Rounded.Folder,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                        },
                        colors = AssistChipDefaults.assistChipColors(
                            containerColor = if (selected) Color(0xFFFFE3EC) else Color.White,
                            labelColor = Color(0xFF54373A)
                        )
                    )
                }
            }

            if (state.isLoading) {
                Box(modifier = Modifier.fillMaxWidth().padding(top = 32.dp), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else if (state.items.isEmpty()) {
                EmptyGallery()
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Adaptive(minSize = 150.dp),
                    modifier = Modifier.fillMaxSize(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(state.items, key = { it.relativePath }) { item ->
                        MediaCard(baseUrl = state.baseUrl, item = item)
                    }
                }
            }
        }
    }
}

@Composable
fun EmptyGallery() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 24.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(Color.White)
            .padding(28.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Nenhuma mídia nesta pasta ainda.", fontWeight = FontWeight.SemiBold)
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Use o botão Enviar mídia para mandar fotos e vídeos para o PC.",
                color = Color(0xFF776966)
            )
        }
    }
}

@Composable
fun MediaCard(baseUrl: String, item: MediaItem) {
    ElevatedCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp)
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(170.dp)
                    .background(Color(0xFFF8EEF1)),
                contentAlignment = Alignment.Center
            ) {
                if (item.type == "image") {
                    AsyncImage(
                        model = baseUrl.trimEnd('/') + item.mediaUrl,
                        contentDescription = item.name,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                } else {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            imageVector = Icons.Rounded.PlayCircle,
                            contentDescription = null,
                            modifier = Modifier.size(54.dp),
                            tint = Color(0xFFCC6C8E)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("Vídeo", fontWeight = FontWeight.Bold)
                    }
                }
            }
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = item.name,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = formatBytes(item.sizeBytes),
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF7C6D6A)
                )
            }
        }
    }
}

fun formatBytes(bytes: Long): String {
    if (bytes < 1024) return "$bytes B"
    val kb = bytes / 1024.0
    if (kb < 1024) return String.format("%.1f KB", kb)
    val mb = kb / 1024.0
    if (mb < 1024) return String.format("%.1f MB", mb)
    val gb = mb / 1024.0
    return String.format("%.1f GB", gb)
}

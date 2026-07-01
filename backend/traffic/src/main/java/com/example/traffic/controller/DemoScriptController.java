package com.example.traffic.controller;

import com.example.traffic.dto.request.DemoScriptRunRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.DemoScriptRunResponse;
import com.example.traffic.service.DemoScriptService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/demo/scripts")
@RequiredArgsConstructor
public class DemoScriptController {

    private final DemoScriptService demoScriptService;

    @PostMapping("/{scriptId}/run")
    public ResponseEntity<CommonResponse<DemoScriptRunResponse>> runScript(
            @PathVariable String scriptId,
            @Valid @RequestBody DemoScriptRunRequest request
    ) {
        DemoScriptRunResponse response = demoScriptService.run(scriptId, request.dataSource());
        return ResponseEntity.ok(CommonResponse.success(response, "Demo script execution completed."));
    }
}